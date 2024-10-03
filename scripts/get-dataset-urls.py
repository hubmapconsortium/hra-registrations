import subprocess
import json

# List of HuBMAP dataset IDs, one entry per line
dataset_ids = [
    "HBM575.THQM.284",
    "HBM462.JKCN.863",
    "HBM334.QWFV.953",
    "HBM938.KMNW.825",
    "HBM899.KTQM.246",
    "HBM934.KLGL.584",
    "HBM394.VSKR.883",
    "HBM945.FSHR.864",
    "HBM439.WJDV.974",
    "HBM353.NZVQ.793",
    "HBM438.JXJW.249",
    "HBM683.NRPR.962",
    "HBM666.RBCG.529",
    "HBM727.DMKG.675",
    "HBM785.FJVT.469",
    "HBM845.VMSZ.536",
    "HBM964.FPNH.767",
    "HBM739.HCWP.359",
    "HBM424.STVV.842",
    "HBM729.XTBN.693",
    "HBM893.MCGS.487",
    "HBM687.SJLD.889",
    "HBM996.MDQH.988",
    "HBM443.LGZK.435",
    "HBM429.LLRT.546",
    "HBM622.STKS.394",
    "HBM792.FFJT.499",
    "HBM742.NHHQ.357",
    "HBM466.XSKL.867",
    "HBM676.QVGZ.455",
    "HBM284.SBPR.357",
    "HBM953.KMTG.758",
    "HBM573.TTLG.748",
    "HBM295.SWJJ.888",
    "HBM865.VDXC.862",
    "HBM288.BBKK.828",
    "HBM565.LSMX.645",
    "HBM832.ZSQJ.442",
    "HBM363.CKHC.928",
    "HBM974.CNWK.327",
    "HBM242.LSCK.393",
    "HBM852.NKST.623",
    "HBM627.KDHD.293",
    "HBM235.VKNJ.237",
    "HBM626.VJMB.795",
    "HBM827.SJBP.777",
    "HBM395.NQKF.566",
    "HBM569.NBHZ.832",
    "HBM297.MZZX.824",
    "HBM823.RJNG.364",
    "HBM447.MNKW.592",
    "HBM488.CNNZ.544",
    "HBM238.GTNW.259",
    "HBM666.NDQZ.365",
    "HBM285.VFDT.966",
    "HBM772.TKCN.287",
    "HBM465.ZNVW.226",
    "HBM824.XGWZ.857",
    "HBM363.LLBL.252",
    "HBM679.NNNK.283",
    "HBM535.QNTP.246",
    "HBM749.SMWP.555",
    "HBM573.SWGH.988",
    "HBM473.QGDG.848"
]

def get_doi_url(dataset_id):
    # Execute the curl command and capture the output
    curl_command = [
        'curl', '-s', '-X', 'GET', 
        f'https://entity.api.hubmapconsortium.org/entities/{dataset_id}', 
        '-H', 'accept: application/json'
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True, check=True)
        json_output = json.loads(result.stdout)
        
        # Extract the doi_url part
        doi_url = json_output.get('doi_url', 'No DOI URL found')
        return doi_url
    except subprocess.CalledProcessError as e:
        return f"Failed to retrieve data for {dataset_id}: {e}"
    except json.JSONDecodeError:
        return f"Invalid JSON response for {dataset_id}"

if __name__ == "__main__":
    for dataset_id in dataset_ids:
        doi_url = get_doi_url(dataset_id)
        print(f"{doi_url}")
