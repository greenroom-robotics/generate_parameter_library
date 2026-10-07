use std::{
    env,
    path::{Path, PathBuf},
    process::Command,
};

const GENERATOR: &str = "generate_parameter_library_rust";

/// Generates `$OUT_DIR/<yaml file stem>.rs` from a parameter yaml file, for use from a `build.rs`.
///
/// `validation_module` is the path of a module holding custom validators and parsers,
/// e.g. `Some("crate::custom")`.
pub fn generate(yaml: impl AsRef<Path>, validation_module: Option<&str>) {
    let yaml = yaml.as_ref();
    let stem = yaml
        .file_stem()
        .unwrap_or_else(|| panic!("{} has no file name", yaml.display()));
    let out = PathBuf::from(env::var_os("OUT_DIR").expect("OUT_DIR is only set for build scripts"))
        .join(stem)
        .with_extension("rs");
    let generator = find_generator();

    let status = Command::new(&generator)
        .arg(&out)
        .arg(yaml)
        .args(validation_module)
        .status()
        .unwrap_or_else(|e| panic!("failed to run {}: {e}", generator.display()));
    assert!(
        status.success(),
        "parameter generation failed for {}",
        yaml.display()
    );

    println!("cargo:rerun-if-changed={}", yaml.display());
    println!("cargo:rerun-if-changed={}", generator.display());
}

fn find_generator() -> PathBuf {
    env::var_os("PATH")
        .iter()
        .flat_map(env::split_paths)
        .map(|dir| dir.join(GENERATOR))
        .find(|candidate| candidate.is_file())
        .unwrap_or_else(|| {
            panic!("{GENERATOR} not found on PATH, is generate_parameter_library_py installed?")
        })
}
