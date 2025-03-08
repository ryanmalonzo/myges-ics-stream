{
  description = "Python environment with dependencies from requirements.txt";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      system = "aarch64-darwin";
      pkgs = import nixpkgs { inherit system; };
      python = pkgs.python312; # Change version as needed
    in {
      devShells.${system}.default = pkgs.mkShell {
        buildInputs = [
          python
          pkgs.python312Packages.pip
        ];
        shellHook = ''
          if [ ! -d .venv ]; then
            python -m venv .venv
            source .venv/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
          else
            source .venv/bin/activate
          fi
        '';
      };
    };
}
