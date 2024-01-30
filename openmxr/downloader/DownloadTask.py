import concurrent.futures
from click import progressbar
import requests
import io
from tqdm.notebook import tqdm

class DownloadTask:
    progress_bar: tqdm
    url: str
    chunk_size:int
    
    def get_size(self, url):
        response = requests.head(url)
        size = int(response.headers['Content-Length'])
        return size

    def download_range(self, url, start, end, id):
        headers = {'Range': f'bytes={start}-{end}'}
        response = requests.get(url, headers=headers)
        output = io.BytesIO()
        for part in response.iter_content(1024):
            output.write(part)
            self.progress_bar.update(len(part))
        return output

    def run_async_functions_asyncio(self, url):
        file_size = self.get_size(url)
        self.progress_bar = tqdm(total=file_size, unit='B', unit_scale=True)
        chunks = range(0, file_size, self.chunk_size)
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
            futures = {executor.submit(self.download_range, url, start, start + self.chunk_size - 1, i): (self.download_range, (url, start, start + self.chunk_size - 1, i)) for i, start in enumerate(chunks)}
            concurrent.futures.wait(futures.keys())
            self.progress_bar.close()

            results = []
            intermediate = []
            for future in concurrent.futures.as_completed(futures):
                _, args = futures[future]
                result = future.result()
                intermediate.append((args[3], result))
        results = [a[1] for a in list(sorted(intermediate, key=lambda x:x[0]))]
        return results

    def __init__(self, url:str, chunk_size:int=1000000):
        self.url = url
        self.chunk_size = chunk_size        
    
    def start(self):        
        results = self.run_async_functions_asyncio(self.url)
        buffer = bytes()
        for result in results:
            buffer+=result.getvalue()
        return buffer