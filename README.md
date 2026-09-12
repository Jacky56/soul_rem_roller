# soul_rem_roller

versions 
```text
python3.11
```


setup
```sh
git clone https://github.com/Jacky56/soul_rem_roller.git
cd ./soul_rem_roller
python3 -m pip install -r requirements.txt
```

install [cudnn v9+](https://developer.nvidia.com/cudnn-downloads) and [cuda v13+](https://developer.nvidia.com/cuda-downloads) for optional gpu runtimes (you can use **CPU** but it is slower).

If you get a not found error, you could [edit these lines](./src/ocr.py#L3-L5) to inject the DDLs for the onnx runtime. 

edit mod list under `./mod_list.yaml`


press `q` or or `Esc` to end the program.

upon hitting any mods on the list, the game will close itself.