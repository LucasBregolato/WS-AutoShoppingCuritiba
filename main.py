import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os

class AutoShoppingCuritiba:

    def __init__(self):
        
        self.headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'}
        self.domain = "https://www.autoshoppingcuritiba.com.br"
        self.base_url = "https://www.autoshoppingcuritiba.com.br/search/pagina."

    def _get_links(self, i=1):
        hrefs = []

        try:
            r = requests.get(self.base_url + str(i), headers=self.headers)
            r.raise_for_status()
            soup = BeautifulSoup(r.content, 'html.parser')
            content = soup.find_all('a', class_="card__figure", href=True)

            if content:
                hrefs = [link['href'] for link in content]
                hrefs += self._get_links(i + 1)
            else:
                print("O processo parou na página:", i)

        except requests.RequestException as e:
            print(f"Erro ao acessar a página {i}: {e}")

        return hrefs
    
    def _save_to_json(self, data, filename, save_dir="data"):

        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Dados salvos em {filepath}")

    def _get_content_from_link(self, i=1):

        links = self._get_links(i=i)
        batch_size = len(links)
        
        for index in range(0, batch_size, batch_size):
            batch_links = links[index:index + batch_size]
            all_data = []

            for link in batch_links:
                url = self.domain + link

                try:
                    r = requests.get(url, headers=self.headers)
                    r.raise_for_status()
                    soup = BeautifulSoup(r.content, 'html.parser')

                    raw_data = soup.find('div', class_="vehicle__card")
                    brand = raw_data.find(class_="vehicle__model").text
                    model = raw_data.find("div", class_="vehicle__model__strong").text
                    version = raw_data.find(class_="vehicle__version").text
                    price = raw_data.find(class_="vehicle__sell__value").text

                    if model in brand:
                        brand = brand.replace(model, "") 
                        brand = re.sub(r'\b\s', "", brand)

                    technical_data_for_validate = raw_data.find_all(class_="vehicle__technical__information__type")
                    technical_data = raw_data.find_all(class_="vehicle__technical__information__value")

                    if technical_data_for_validate[6].text == "Cilindradas":
                        year = technical_data[0].text
                        status = technical_data[1].text
                        color = technical_data[2].text
                        fuel = technical_data[3].text
                        km = technical_data[4].text
                        plate = technical_data[5].text
                        cc = technical_data[6].text
                        colling = technical_data[7].text
                        data = {
                            "vehicle_type": "motorcycle",
                            "id": link[-6:],
                            "brand" : brand,
                            "model": model,
                            "version": version,
                            "price" : price,
                            "year": year,
                            "status": status,
                            "color": color,
                            "km": km,
                            "cc": cc,
                            "plate": plate,
                            "fuel": fuel,
                            "colling": colling
                        }
                    else:
                        year = technical_data[0].text
                        status = technical_data[1].text
                        color = technical_data[2].text
                        km = technical_data[3].text
                        type_strucutre = technical_data[4].text
                        transmission = technical_data[5].text
                        fuel = technical_data[6].text
                        doors = technical_data[7].text
                        data = {
                            "vehicle_type": "car",
                            "id": link[-6:],
                            "brand" : brand,
                            "model": model,
                            "version": version,
                            "price" : price,
                            "year": year,
                            "status": status,
                            "color": color,
                            "km": km,
                            "type": type_strucutre,
                            "transmission": transmission,
                            "fuel": fuel,
                            "doors": doors
                        }

                    all_data.append(data)

                except requests.RequestException as e:
                    print(f"Erro ao acessar o link {url}: {e}")

                except Exception as e:
                    print(f"Erro ao processar o link {url}: {e}")

            filename = f"batch_{i}.json"
            self._save_to_json(all_data, filename)
            time.sleep(2)

if __name__ == "__main__":
    data = AutoShoppingCuritiba()

    #If not defined, 'i' will run from 1 to 71 and generate a lot of records in the JSON file.
    data._get_content_from_link(i=70)