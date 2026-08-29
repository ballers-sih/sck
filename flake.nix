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
          nativeBuildInputs = [
            pkgs.qt6.wrapQtAppsHook
          ];
          buildInputs = [
            pkgs.qt6.qtbase
          ];
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

          shellHook = ''
            set -a
            source .env || true
            set +a

            export SCKD_ADDRESS=127.0.0.1
            export SCKD_PORT=7079

            export ROBERTA_MODEL="$PWD/.models/roberta-email-fraud-detector"
            hf download cunxin/roberta-email-fraud-detector --local-dir "$ROBERTA_MODEL"

            export CLAMAV_DB="$PWD/.clamav"

            mkdir -p "$CLAMAV_DB"

            if ! compgen -G "$CLAMAV_DB/*.cvd" > /dev/null &&
               ! compgen -G "$CLAMAV_DB/*.cld" > /dev/null; then

              cat > "$CLAMAV_DB/freshclam.conf" <<EOF
            DatabaseDirectory $CLAMAV_DB
            DatabaseOwner $(id -un)
            UpdateLogFile $CLAMAV_DB/freshclam.log
            PidFile $CLAMAV_DB/freshclam.pid
            DatabaseMirror database.clamav.net
            EOF

              echo "ClamAV database not found; downloading it..."
              freshclam --config-file="$CLAMAV_DB/freshclam.conf"
            fi
          '';
        };
      };
    };
}
