from tempfile import TemporaryDirectory
from pathlib import Path
from .core import acquire_local, candidate_variance, canonical_receipt
import json

def main():
    with TemporaryDirectory() as tmp:
        file=Path(tmp)/'synthetic_tow_ticket.txt'
        file.write_text('SYNTHETIC tow ticket T-100, amount 125.00')
        evidence=acquire_local(file,'synthetic-tenant','synthetic demo')
        finding=candidate_variance({'tenant_id':'synthetic-tenant','currency':'USD','amount':'125.00'},
                                   {'tenant_id':'synthetic-tenant','currency':'USD','amount':'120.00'})
        print(json.dumps(canonical_receipt({'evidence':evidence,'finding':finding,'human_review':'PENDING'}),indent=2))

if __name__=='__main__': main()
