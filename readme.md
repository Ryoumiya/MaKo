# MaKo

## Manga and Comic Cutter
A simple manga or comic cutter using python and opencv

### Quick use guide
the `-o` argument is optional if uncalled then it would use the current directory
```
python3 mako.py -i path/to/img.jpg
python3 mako.py -i path/to/img.jpg -o /path/to/output/dir/
python3 mako.py -i /path/to/folder -o /path/to/output/dir/
```
### Todo List
[] More output types
[] GUI 
[] More Panel type support

### Additional info on args
`-t` for input type `comic` or `manga` which define the numbering pattern 
```
python3 mako.py -i file.jpg -t comic 
python3 mako.py -i file.jpg -t manga
```
by default `manga` is used 