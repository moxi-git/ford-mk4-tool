## Installation

1. clone the repo & cd into ford-mk4-tool
  ```bash
  git clone https://github.com/moxi-git/ford-mk4-tool.git
  cd ford-mk4-tool
  ```

2. run some scripts
   ```bash
   ./env-setup.sh
   ```
or

  ```bash
  ./env-setup.fish
  ```

3. run the program
   eathier run-gui.sh/.fish or run.sh/.fish
   ```bash
   .run-gui.sh
   .run.sh
   ./run-gui.fish
   ./run.fish
   ```

> [!NOTE]
> if you come back to the project is not working just run
```bash
source .venv/bin/activate
```

or

```bash
source .venv/bin/actiavte.fish
```

## Download Pre-built:
download from [Releases](https://github.com/moxi-git/ford-mk4-tool/releases)

then

just extract with 7z

```bash
7z x main.7z
```

or

```
7z x main-gui.7z
```

then run

```bash
./main
./main-gui
```
