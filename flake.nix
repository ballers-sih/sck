{
  description = "sck - scam check";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs { inherit system; };
      python = pkgs.python3Packages;
    in
    {
      packages.${system}.default = python.buildPythonApplication {
        pname = "sck";
        version = "0";
        src = ./.;
        pyproject = true;
        build-system = [
          python.setuptools
        ];
        dependencies = [
          python.python-dotenv
        ];
      };
    };
}
