mod parameters {
    include!(concat!(env!("OUT_DIR"), "/parameters.rs"));
}

mod custom {
    pub fn is_odd(value: i64) -> Result<(), String> {
        if value % 2 == 1 {
            Ok(())
        } else {
            Err(format!("value {value} must be odd"))
        }
    }

    #[derive(Clone, Debug, PartialEq)]
    pub struct HostName(String);

    impl TryFrom<&str> for HostName {
        type Error = String;

        fn try_from(value: &str) -> Result<Self, String> {
            let valid = !value.is_empty()
                && value.split('.').all(|label| {
                    !label.is_empty() && label.chars().all(|c| c.is_ascii_alphanumeric() || c == '-')
                });
            if valid {
                Ok(Self(value.to_owned()))
            } else {
                Err(format!("'{value}' is not a valid host name"))
            }
        }
    }

    #[derive(Clone, Debug, PartialEq)]
    pub struct Port(u16);

    impl Port {
        pub fn new(value: i64) -> Result<Self, String> {
            match u16::try_from(value) {
                Ok(port) if port != 0 => Ok(Self(port)),
                _ => Err(format!("{value} is not a valid port")),
            }
        }
    }
}

use std::{sync::Mutex, time::Duration};

use rclrs::{Context, CreateBasicExecutor, RclrsError, RclrsErrorFilter, SpinOptions};

fn main() -> Result<(), RclrsError> {
    let mut executor = Context::default_from_env()?.create_basic_executor();
    let node = executor.create_node("example_rust")?;
    let listener = parameters::ParamListener::new(&node, "")
        .unwrap_or_else(|e| panic!("failed to declare parameters: {e}"));

    let params = Mutex::new(listener.get_params());
    println!("initial: {:?}", params.lock().unwrap());

    let _timer = node.create_timer_repeating(Duration::from_millis(100), move || {
        let mut params = params.lock().unwrap();
        if listener.is_old(&params) {
            *params = listener.get_params();
            println!("updated: {params:?}");
        }
    })?;

    executor.spin(SpinOptions::default()).first_error()
}
