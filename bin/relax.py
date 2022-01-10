"""Скрипт для запуска процесс релаксации структур в MOPAC"""
import os
import shutil
import zlib
from tqdm.auto import tqdm
import pickle
import argparse
import asyncio
from runmopac.misc import get_log
from runmopac.utils import save_mop, parse_out


DIR = os.path.split(os.path.abspath(__file__))[0]
DIR_LOG = os.path.join(DIR, 'log')
DIR_EXCHANGE = os.path.join(DIR, 'exchange')

LOG = get_log(DIR_LOG, __file__.split('.')[0])

MOPAC_RUN = '/opt/mopac/MOPAC2016.exe {}'.format


def read_dataset(path_to_file):
    with open(path_to_file, 'rb') as fp:
        dataset = pickle.load(fp)
    return dataset


def filter_dataset(dataset, output_file):
    output = read_output(output_file)
    filenames = {v['filename'] for v in output}
    dataset = [v for v in dataset if v['filename'] not in filenames]
    return dataset

def read_output(path_to_file):
    dataset = []
    with open(path_to_file, 'rb') as fp:
        while True:
            try:
                dataset.extend(pickle.load(fp))
            except EOFError:
                break
    return dataset


def write_output(path_to_file, dataset):
    with open(path_to_file, 'ab') as fp:
        pickle.dump(dataset, fp)


async def relax(filename, ids, xyz):
    filename_mop = os.path.join(DIR_EXCHANGE, filename + '.mop')
    filename_out = os.path.join(DIR_EXCHANGE, filename + '.out')
    filename_arc = os.path.join(DIR_EXCHANGE, filename + '.arc')
    save_mop(ids, xyz, filename_mop)

    proc = await asyncio.create_subprocess_shell(
        MOPAC_RUN(filename_mop),
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()
    output = {
        'filename': filename,
        'returncode': proc.returncode,
        'stdout': stdout.decode(),
        'stderr': stderr.decode(),
    }

    try:
        with open(filename_out, 'r') as fp:
            text = fp.read()
        output['out'] = zlib.compress(text.encode())

        total_energy, ids, xyz = parse_out(text)
        output.update({
                'energy': total_energy,
                'ids': ids,
                'xyz': xyz
            })
    except Exception:
        LOG.exception(f"problem with output file: {filename_out}")
    try:
        with open(filename_arc, 'r') as fp:
            output['arc'] = zlib.compress(fp.read().encode())
    except Exception:
        LOG.exception(f"problem with arc file: {filename_arc}")
    try:
        os.remove(filename_mop)
        os.remove(filename_out)
        os.remove(filename_arc)
    except Exception:
        LOG.exception("Can't remove files")
    return output


async def main(
        input_file,
        output_file,
        n_jobs,
        batch_size=None,
        pbar=None):
    """
    Args:
        input_file (str): path to file with input data
        output_file (str): path to file to save output data
        n_jobs (int): the number of workers
        batch_size (int): the number of calculated data to save
        pbar (tqdm): progres bar
    """
    LOG.info('start to relax')
    LOG.info(f'create exchange dir: {DIR_EXCHANGE}')
    os.makedirs(DIR_EXCHANGE, exist_ok=True)

    LOG.info(f'read input file: {input_file}')
    dataset = read_dataset(input_file)

    if os.path.isfile(os.path.join(DIR, output_file)):
        dataset = filter_dataset(dataset, os.path.join(DIR, output_file))

    if pbar is not None:
        pbar.total = len(dataset)

    done = asyncio.Queue()

    count_put, count_get = 0, 0
    batch = []
    while count_get < len(dataset):
        while count_put - count_get < n_jobs and count_put < len(dataset):
            data = dataset[count_put]
            f = asyncio.ensure_future(
                asyncio.create_task(
                    relax(
                        filename=data['filename'],
                        ids=data['ids'],
                        xyz=data['xyz']
                    )))
            f.add_done_callback(lambda v: done.put_nowait(v))
            count_put += 1
        r = await done.get()
        count_get += 1

        batch.append(r.result())
        if batch_size is not None and len(batch) >= batch_size:
            write_output(os.path.join(DIR, output_file), batch)
            batch = []

        if pbar is not None:
            pbar.update(1)

    if batch:
        write_output(os.path.join(DIR, output_file), batch)
        batch = []

    LOG.info(f'remove exchange dir: {DIR_EXCHANGE}')
    shutil.rmtree(DIR_EXCHANGE, ignore_errors=True)
    LOG.info('finish to relax')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', dest='input', required=True, type=str)
    parser.add_argument('--output', dest='output', default='output.pkl', type=str)
    parser.add_argument('--n_jobs', dest='n_jobs', required=True, type=int)
    parser.add_argument('--batch_size', dest='batch_size', default=4, type=int)

    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    with tqdm() as pbar:
        loop.run_until_complete(main(
            input_file=args.input,
            output_file=args.output,
            n_jobs=args.n_jobs,
            batch_size=args.batch_size,
            pbar=pbar
        ))
    loop.run_until_complete(asyncio.sleep(1.0))
    loop.close()
