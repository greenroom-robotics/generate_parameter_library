use std::{env, path::PathBuf, process::Command};

fn main() {
    let yaml = "src/parameters.yaml";
    let out = PathBuf::from(env::var("OUT_DIR").unwrap()).join("parameters.rs");
    let status = Command::new("generate_parameter_library_rust")
        .arg(&out)
        .arg(yaml)
        .arg("crate::custom")
        .status()
        .expect("generate_parameter_library_rust not found, is generate_parameter_library_py installed?");
    assert!(status.success(), "parameter generation failed");
    println!("cargo:rerun-if-changed={yaml}");
}
