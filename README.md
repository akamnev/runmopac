# Программа для прогона структур через MOPAC

Подразумевается, что MOPAC поставлен по пути `/opt/mopac/MOPAC2016.exe`
Для установки программы заходим в корень и выполняем команду 
```shell
pip install -e .
```
Создать папку `log` в директории `bin`
```shell
cd ./bin
mkdir log
```
Для запуска расчета необходимо из папки `bin` выполнять комманду
```shell
python relax.py --input=path_to_input_file --output=path_to_output_file --n_jobs=40 --batch_size=128 --max_relax_time=300
```
Если `output` файл существует, то соответствующие данные из `input` файла считаться не будут.


Данные должны быть сохранены в pickle в виде списка словарей с полями:
* filename - уникальное название структуры; 
* ids - список id атомов;
* xyz - список списков координат.

Опционально, установить `virtualenv`
```shell
sudo apt install python3-virtualenv
```
Создать и запустить виртуальное окружение
```shell
virtualenv ~/venv/runmopac --python=python3
source ~/venv/runmopac/bin/activate
```

## Запуск в одном потоке
Последняя версия MOPAC использует MKL которым сама плохо управляет, 
а библиотека запускает расчет на всех ядрах. Для ограничения на
использования ядер MKL необходимо поставить соответствующую переменную
```shell
export MKL_NUM_THREADS=1
```