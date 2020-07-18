# pDeep2
Forked from https://github.com/pFindStudio/pDeep/tree/master/pDeep2.
For information on features, usage, and requirements of pDeep and pDeep2 in general, please refer to the readme in the original repository.  
## Server Version 
This project extends pDeep2 by a web server interface that allows you to remotely predict tandem mass spectra from a different machine.
In addition to the software required to run pDeep2, `docker` is required.
Prior to using the server version of pDeep2, you need to replace the path in the file `../run_pDeep_server.sh`
by the absolute path to the folder containing your trained models. Furthermore, you can customize the script `server.py`
to allow routes to your own models. The port for the server is set to 5050 but can be changed by editing `../Makefile`.
Then, start the server by running `../run_pDeep_server.sh`.  
You can then send a prediction request to the server by calling
``` 
curl -F 'peptides=@<YOUR_PEPTIDES.tsv>'  <IP_ADDRESS_OF_YOUR_SERVER>:5050/tryptic 
```
In case you've added more models in the `server.py` script, you can replace `tryptic` by a different route, 
e.g. `nontryptic/cid`.