## Building

### Setting up enviroment
1. as always you need to clone the repo and cd into the folder

```bash
git clone https://github.com/moxi-git/ford-mk4-tool.git
cd ford-mk4-tool
```

2. install 7z
 ```bash
sudo apt install p7zip-full  # Ubuntu/Debian
sudo dnf install p7zip       # Fedora
sudo pacman -S p7zip         # Arch
 ```

3. setup venv
   ```bash
   ./env-setup.sh
   ```
or

  ```bash
  ./env-setup.fish
  ```

4. to be safe re-run venv by running command down bellow
   ```bash
   source .venv/bin/activate
   ```

or

   ```bash
   source .venv/bin/activate.fish
   ```

### Building

   ```bash
   build.sh
   ```

or

  ```bash
  build.fish
  ```

## Cleaning
```bash
clean.sh
```
or
```bash
clean.fish
```

### Notes
> [!NOTE]
> if you come back to the project is not working just run
```bash
source .venv/bin/activate
```

or

```bash
source .venv/bin/actiavte.fish
```
