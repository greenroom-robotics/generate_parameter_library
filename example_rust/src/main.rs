mod parameters {
    include!(concat!(env!("OUT_DIR"), "/parameters.rs"));
}

mod custom_validators {
    pub fn is_odd(value: i64) -> Result<(), String> {
        if value % 2 == 1 {
            Ok(())
        } else {
            Err(format!("value {value} must be odd"))
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
