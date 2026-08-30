{
  description = "sck - scam check";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs { inherit system; };
      python = pkgs.python3Packages;
    in
    {
      packages.${system} = rec {
        default = sck;
        sck = python.buildPythonApplication {
          pname = "sck";
          version = "0";
          src = ./.;
          pyproject = true;
          build-system = [ python.setuptools ];
          dependencies = [
            python.python-dotenv
            python.torch
            python.transformers
            python.pyqt6
          ];
          nativeBuildInputs = [ pkgs.qt6.wrapQtAppsHook ];
          buildInputs = [ pkgs.qt6.qtbase ];
        };
      };
      devShells.${system} = rec {
        default = sck;
        sck = pkgs.mkShell {
          packages = [
            pkgs.clamav
            pkgs.python3
            python.huggingface-hub
          ];

          shellHook = builtins.readFile ./shell-hook.sh;
        };
      };
    };
}
