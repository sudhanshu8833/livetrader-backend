
'''
1. no spaces in symbol
2. symbol should be in uppercase
3. no '.' in symbol
'''
from ingest_in_db import ingest_data
from helper import get_all_file_names, preprocess_date
import time

index_map = {
    "NIFTY200MOMENTM30.csv": "MOMENTUM20030.csv",
    "NIFTYMIDLIQ.csv": "MIDCAPLIQUIDITY.csv",
    "NIFTY GS 10YR CLN.csv": "GS10YRCLN.csv",
    "NIFTY100 LOWVOL30.csv": "LOWVOL10030.csv",
    "NIFTY MIDCAP 150.csv": "MIDCAP150.csv",
    "MIDCPNIFTY.csv": "MIDCAPNIFTY.csv",
    "NIFTYPSE.csv": "PSU.csv",
    "NIFTY50 PR 1X INV.csv": "NIFTY50PR1XINV.csv",
    ".NSEI.csv": "NIFTY.csv",
    "NIFTYSERVICE.csv": "SERVICE.csv",
    "NIFTY LARGEMID250.csv": "LARGEMID250.csv",
    "NIFTYMETAL.csv": "METAL.csv",
    "NIFTY100 EQL WGT.csv": "EQUALWEIGHT100.csv",
    "NIFTY HEALTHCARE.csv": "HEALTHCARE.csv",
    "NIFTYREALTY.csv": "REALTY.csv",
    "NIFTYNEXT.csv": "NEXT50.csv",
    "NIFTY200 ALPHA 30.csv": "ALPHA20030.csv",
    "NIFTYDIV.csv": "DIVIDEND.csv",
    "NIFTY SMLCAP 50.csv": "SMALLCAP50.csv",
    "NIFTY ALPHA 50.csv": "ALPHA50.csv",
    "NIFTYPVTBANK.csv": "PVTBANK.csv",
    "NIFTY MIDSML 400.csv": "MIDSMALL400.csv",
    "NIFTY INDIA MFG.csv": "INDIAMANUFACTURING.csv",
    "NIFTY50 TR 2X LEV.csv": "NIFTY50TR2XLEV.csv",
    "NIFTY CONSR DURBL.csv": "CONSUMERDURABLES.csv",
    "NIFTY200 QUALTY30.csv": "QUALITY20030.csv",
    "NIFTYPSUBANK.csv": "PSUBANK.csv",
    "NIFTY FINSRV25 50.csv": "FINANCIALSERVICES2550.csv",
    "NIFTY TOTAL MKT.csv": "TOTALMARKET.csv",
    "NIFTYAUTO.csv": "AUTO.csv",
    "NIFTY MICROCAP250.csv": "MICROCAP250.csv",
    "CPSEINDEX.csv": "CPSE.csv",
    "NIFTY GS 15YRPLUS.csv": "GS15YRPLUS.csv",
    "NIFTY GS 8 13YR.csv": "GS8TO13YR.csv",
    "NIFTY500 MULTICAP.csv": "MULTICAP500.csv",
    "NIFTY M150 QLTY50.csv": "MID150QUALITY50.csv",
    "NIFTY GS 10YR.csv": "GS10YR.csv",
    ".NSEBANK.csv": "BANKNIFTY.csv",
    "INDIAVIX.csv": "VIX.csv",
    "NIFTYPHARMA.csv": "PHARMA.csv",
    "NIFTYM150MOMNTM50.csv": "MID150MOMENTUM50.csv",
    "NIFTYMEDIA.csv": "MEDIA.csv",
    "NIFTYMNC.csv": "MNC.csv",
    "NIFTY GS 4 8YR.csv": "GS4TO8YR.csv",
    "NIFTY GS COMPSITE.csv": "GSCOMPOSITE.csv",
    "NIFTY100ESGSECLDR.csv": "ESGSECTORLEADERS100.csv",
    "NIFTY50 TR 1X INV.csv": "NIFTY50TR1XINV.csv",
    "NIFTY ALPHALOWVOL.csv": "ALPHALOWVOL.csv",
    "NIFTY50 EQL WGT.csv": "EQUALWEIGHT50.csv",
    "NIFTY GROWSECT 15.csv": "GROWTHSECTOR15.csv",
    "NIFTY100 ESG.csv": "ESG100.csv",
    "NIFTYCONS.csv": "CONSUMER.csv",
    "NIFTY50 PR 2X LEV.csv": "NIFTY50PR2XLEV.csv",
    "NIFTY OIL AND GAS.csv": "OILANDGAS.csv",
    "NIFTY GS 11 15YR.csv": "GS11TO15YR.csv",
    "NIFTYSMALLCAP.csv": "SMALLCAP.csv",
    "NIFTYCOMM.csv": "COMMODITIES.csv",
    "NIFTY100QLY30.csv": "QUALITY10030.csv",
    "NIFTY SMLCAP 250.csv": "SMALLCAP250.csv",
    "NIFTYFINANCE.csv": "FINANCE.csv",
    "NIFTY IND DIGITAL.csv": "INDIADIGITAL.csv",
    "NIFTYENERGY.csv": "ENERGY.csv",
    "NIFTYMID50.csv": "MIDCAP50.csv"
}

csv_files = None

directory = "./index_data"
# csv_files = get_all_file_names(directory)

months = [
    'january',
    'february', 
    'march', 
    'april', 
    'may', 
    'june', 
    'july', 
    'august',
    'september', 
    'october', 
    'november', 
    'december'
]


if __name__ == "__main__":
    
    for month in months:
        time_start = time.time()
        path = directory + '/' + month
        csv_files = get_all_file_names(path)
        resultant_data = []
        for file in csv_files:
            with open(path + '/' + file, 'r') as f:
                lines = f.readlines()
                for line in lines[1:]:
                    result_data = []
                    data = line.split(',')
                    date = preprocess_date(f'{data[1]} {data[2]}')
                    result_data.append(date)
                    data[-1].replace('\n', '')
                    if data[0] + '.csv' in index_map:
                        data[0] = index_map[data[0] + '.csv'][:-4]
                    result_data = result_data + [data[0], float(data[3]), float(data[4]), float(data[5]), float(data[6]), float(data[7])]
                    result_data.append('NSE')
                    resultant_data.append(tuple(result_data))

        print(f"Time taken for calculation of {month} is {time.time() - time_start}")
        temp_time = time.time()
        ingest_data(resultant_data)
        print(f"Time taken for ingestion of {month} is {time.time() - temp_time}")         
