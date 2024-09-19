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

          iso639 = pkgs.python3Packages.buildPythonPackage rec {
            name = "python-iso639";
            pname = "python-iso639";
            version="2024.2.7";
            pyproject=true;

            src = pkgs.python3Packages.fetchPypi {
              inherit pname version;
              sha256 = "sha256-wyMjM0jDTVfGAePm2CQIjkkolry5emGof32TQBowU3c=";
            };
            build-system = [ pkgs.python3Packages.poetry-core ];
            dependencies = [
              pkgs.python3Packages.setuptools
            ];
            propagatedBuildInputs =  [ ];
            # pythonImportsCheck = [  ];
            # pythonRuntimeDepsCheckHook = ''
            #   echo "test"
            # '';

            # pythonRuntimeDepsCheck = ''
            #   ls -lh
            #   echo "hello"
            # '';
            doCheck = false;
          };

          ibmCosSDKCore = pkgs.python3Packages.buildPythonPackage rec {
            name = "ibm-cos-sdk-core";
            pname = "ibm-cos-sdk-core";
            version="2.13.6";
            pyproject=true;

            src = pkgs.python3Packages.fetchPypi {
              inherit pname version;
              hash = "sha256-3UH7eJ7rZVRlAa+rzVDniEarRRO2rUBC5BC2oU/4hBM=";
            };
            build-system = [ pkgs.python3Packages.poetry-core ];
            dependencies = [
              pkgs.python3Packages.setuptools
            ];
            propagatedBuildInputs =  [ ];
            pythonImportsCheck = [  ];
            pythonRuntimeDepsCheckHook = ''
              echo "test"
            '';

            pythonRuntimeDepsCheck = ''
              ls -lh
              echo "hello"
            '';
            doCheck = false;
          };

          ibmCosSDK = pkgs.python3Packages.buildPythonPackage rec {
            name = "ibm-cos-sdk";
            pname = "ibm-cos-sdk";
            version="2.0.1";
            pyproject=true;

            src = pkgs.python3Packages.fetchPypi {
              inherit pname version;
              hash = "sha256-NG0neo50uuggtNagP2EHlst6d/+FQaZztqob0YV6hj4=";
            };
            build-system = [ pkgs.python3Packages.poetry-core ];
            dependencies = [
              pkgs.python3Packages.setuptools
              pkgs.python3Packages.jmespath
              ibmCosSDKCore
            ];
            propagatedBuildInputs =  [ ];
            pythonImportsCheck = [  ];
            pythonRuntimeDepsCheckHook = ''
              echo "test"
            '';

            pythonRuntimeDepsCheck = ''
              ls -lh
              echo "hello"
            '';
            doCheck = false;
          };

          ibmWatsonAI = pkgs.python3Packages.buildPythonPackage rec {
            name = "ibm-watsonx-ai";
            pname = "ibm_watsonx_ai";
            version="1.1.5";
            pyproject=true;

            src = pkgs.python3Packages.fetchPypi {
              inherit pname version;
              hash = "sha256-UGphdTqomT+J3QFNBRr77BwufplhutAfs8yCpRoMGiE=";
            };
            build-system = [ pkgs.python3Packages.poetry-core ];
            dependencies = [
              pkgs.python3Packages.setuptools
              pkgs.python3Packages.pandas
              pkgs.python3Packages.httpx
              pkgs.python3Packages.tabulate
              pkgs.python3Packages.langchain
              pkgs.python3Packages.importlib-metadata
              pkgs.python3Packages.lomond
              ibmCosSDK
            ];
            propagatedBuildInputs =  [ ];
            pythonImportsCheck = [  ];
            pythonRuntimeDepsCheckHook = ''
              echo "test"
            '';

            pythonRuntimeDepsCheck = ''
              ls -lh
              echo "hello"
            '';
            doCheck = false;
          };
          langchain-ibm = pkgs.python3Packages.buildPythonPackage rec {
            name = "langchain-ibm";
            pname = "langchain_ibm";
            version="0.1.12";
            pyproject=true;

            src = pkgs.python3Packages.fetchPypi {
              inherit pname version;
              hash = "sha256-okKNW3dUElv4/YVFslz6r8df9FsHzKFyQT2hxu6QfK4=";
            };

            build-system = [ pkgs.python3Packages.poetry-core ];
            dependencies = [
              ibmWatsonAI
            ];
            propagatedBuildInputs =  [ ];
            pythonImportsCheck = [  ];
            pythonRuntimeDepsCheckHook = ''
              echo "test"
            '';

            pythonRuntimeDepsCheck = ''
              ls -lh
              echo "hello"
            '';
            doCheck = false;
          };

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
            flask_sqlalchemy
            pylint
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
            ibmWatsonAI
            langchain-ibm
            unstructured
            emoji
            iso639
            langdetect
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
              pkgs.kind
            ];

          };
        }
      );
}
