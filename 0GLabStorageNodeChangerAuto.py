import subprocess
import time
from rich.progress import Progress
from playwright.sync_api import sync_playwright

#You can use this however you want as long as you credit us.
#Credits to astrostake for providing the guide and resources to make this happen!!!
#I encourage you to visit their website and check their various amazing resources https://astrostake.xyz/
#I don't know what other ways to get the data, but i used playwright to basically,
# let it load like when you open a website but in the background (i think? i'm a novice srry) and take all the texts.

#put your time in here, it counts 1 as a second, so 1 minute is 60. 12 hours is the default.
time_input = 43200 

try:
     while True:
        #Getting data from astrostake blockRPC
        print("Getting data from astrostake, this might take a while...")
        print("If you wish to cancel or exit press ctrl+c to exit (KeyboardInterrupt)")
        with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto("https://www.astrostake.xyz/networks/0g-labs/endpoints-status/",timeout = 60000)
                page.wait_for_timeout(5000)

                rows = page.locator('tr').all_text_contents()
                data = ""
                for row in rows:
                        data += row
                browser.close()

        first = data.splitlines()
        lines = [line.strip() for line in first if line.strip() != '']
        final = []

        #sorting and filtering
        chunk_size = 7
        dicts = []
        dict_index=0

        unwanted_list = ["Provider","Endpoint","Status","Block Height","Latency (ms)","Peers","Network","Official"]
        name =["Name", "Link" ,"Status" , "Block Height" ,"Latency (ms)", "Peers", "ID"]
        for unwanted in unwanted_list:
                lines.remove(unwanted)

        for i in range(0, len(lines), chunk_size):
            chunk = lines[i:i+chunk_size]
            #slicing i=0, lines[0:7] -> [a,b,c,d,e,f,g], i=7, lines[7:14] -> [h,i,j,k,l,m,n]
            current_dict = {}

            # what does enumerate do? 1 Official RPC - 0G, 2 evmrpc-testnet.0g.ai, 3 Health>
            for j, item in enumerate (chunk):
                key_name = f"{name[j]}{dict_index}"
                current_dict[key_name] = item

            dicts.append(current_dict)
            dict_index += 1

        print (dicts)
        print (f"Total: {dict_index}")

        #filter part 1 (You can probably delete this part, this is more so for checking the variables)
        filtered = []
        for d in dicts:
            for key, value in d.items():
                if "Latency (ms)" in key:
                    try:
                        latency = int(value.replace(',', ''))  
                        if latency < 20:
                            filtered.append(d)
                    except ValueError:
                        continue

        print (filtered)
        lowest_latency_value = None
        lowest_entry = None
        latency_key = None

        #filter part 2
        for entry in filtered:
            for key, value in entry.items():
                if "Latency (ms)" in key:
                    latency_value = int(value) 
                    if lowest_latency_value is None or latency_value < lowest_latency_value:
                        lowest_latency_value = latency_value
                        lowest_entry = entry
                    break

        for key in lowest_entry.keys():
            if "Latency (ms)" in key:
                latency_key = key
                break

        number_suffix = latency_key.replace("Latency (ms)", "")
        name = lowest_entry[f"Name{number_suffix}"]
        link = lowest_entry[f"Link{number_suffix}"]
        link_usable = ("https://" + link)

        print("Lowest latency number:", number_suffix)
        print("Name: ", name)
        print(f"Link: {link_usable}")
        print (type(link))

        #running the changing of RPC links (Much love to astrostake for making it easier to change RPC)
        rpc_link = link_usable
        cmd = f"echo '{rpc_link}' | bash <(wget -qO- https://raw.githubusercontent.com/astrostake/0G-Labs-script/refs/heads/main/storage-node/change_storage_rpc.sh)"

        subprocess.run(["bash", "-c", cmd])

        with Progress() as progress:
            task = progress.add_task("[cyan]Counting Down...", total = time_input)
            for i in range(time_input):
                time.sleep(1)
                progress.update(task,advance=1)
    
except KeyboardInterrupt:
    print ("Stopped By User, Thank you for using my program :D")