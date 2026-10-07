fn main() {
    generate_parameter_library_rs::generate("src/parameters.yaml", Some("crate::custom"));
}
