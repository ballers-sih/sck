{
  description = "sck - scam check";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs { inherit system; };
    in
    {
      packages.${system}.default = pkgs.python3Packages.buildPythonApplication {
        pname = "sck";
        version = "0";
        src = ./.;
        pyproject = true;
        build-system = [
          pkgs.python3Packages.setuptools
        ];
      };
    };
}
