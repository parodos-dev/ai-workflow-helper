{
  description = "Langchain flake with tools";
  inputs = {
    #nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.05";
    #nixpkgs.url = "github:NixOS/nixpkgs/nixos-unestable";
    nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs {
            inherit system;
          };
          python-packages = ps: with ps; [
            beautifulsoup4
            click
            faiss
            ipdb
            ipython
            jsonschema
            langchain
            langchain-community
            ollama
            openai
            tiktoken
            flake8
            wikipedia
            pip
            (langchain.overridePythonAttrs (prevAttrs: {
              name = "langchain-experimental";
              sourceRoot = "${prevAttrs.src.name}/libs/experimental";
              dependencies = [
                langchain
                langchain-community
              ];
              pythonImportsCheck = [ ];

              pythonRuntimeDepsCheck = ''
              echo "hello"
              '';
              doCheck = false;
            }))
            (langchain.overridePythonAttrs (prevAttrs: {
              name = "langchain-openai";
              sourceRoot = "${prevAttrs.src.name}/libs/partners/openai";
              dependencies = [
                langchain
                langchain-community
                openai
                tiktoken
              ];
              pythonImportsCheck = [ ];

              pythonRuntimeDepsCheck = ''
              echo "hello"
              '';
              doCheck = false;
            }))
          ];

        in
        with pkgs;
        {
          devShells.default = mkShell {
            buildInputs = [
              (pkgs.python3.withPackages python-packages)
              pkgs.gnumake
              pyright
              pkgs.direnv
            ];

          };
        }
      );
}
