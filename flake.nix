{
  description = "sck - scam check";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";

  outputs =
    inputs:
    let
      system = "x86_64-linux";
      pkgs = import inputs.nixpkgs { inherit system; };
      python = pkgs.python3Packages;

      shell-hook = ''
        PATH=${pkgs.clamav}/bin:${python.huggingface-hub}/bin:${pkgs.coreutils}/bin
        ${builtins.readFile ./shell-hook.sh}
      '';
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
            python.requests
          ];
          nativeBuildInputs = [ pkgs.qt6.wrapQtAppsHook ];
          buildInputs = [ pkgs.qt6.qtbase ];
        };
        sckd = pkgs.writeShellScriptBin "sckd" ''
          ${shell-hook}
          ${sck}/bin/sckd
        '';
        sck_cli = pkgs.writeShellScriptBin "sck_cli" "${sck}/bin/sck_cli";
        sck_gui = pkgs.writeShellScriptBin "sck_gui" "${sck}/bin/sck_gui";
        sck_imapd = pkgs.writeShellScriptBin "sck_imapd" "${sck}/bin/sck_imapd";
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
