{ pkgs, ... }: {
  # Which nixpkgs channel to use (stable is safer)
  channel = "stable-24.11";

  # Packages to install in your environment
  packages = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.nodejs_20
  ];

  # Sets environment variables
  env = {
    # You can add your GEMINI_API_KEY here if you want it persistent
    # GEMINI_API_KEY = "your-key-here";
  };

  idx = {
    # Extensions you want from the Marketplace
    extensions = [
      "ms-python.python"
      "tamasfe.even-better-toml"
    ];

    workspace = {
      # Runs when the workspace is FIRST created
      onCreate = {
        install-gemini = "npm install -g @google/gemini-cli";
        # This clones conductor into the hidden gemini folder
        setup-conductor = "mkdir -p ~/.gemini/extensions && git clone https://github.com/gemini-cli-extensions/conductor.git ~/.gemini/extensions/conductor";
      };

      # Runs EVERY TIME you open the workspace
      onStart = {
        link-conductor = "gemini extensions link ~/.gemini/extensions/conductor";
      };
    };
  };
}