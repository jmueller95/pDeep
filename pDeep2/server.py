import warnings
import flask
from flask import after_this_request
import pDeep2.model.fragmentation_config as fconfig
import pDeep2.model.load_data as load_data
from pDeep2.model.bucket_utils import write_buckets_mgf
import pDeep2.model.lstm_tf as lstm
import argparse
import time
import tempfile

app = flask.Flask(__name__)
model_folder = "/root/tf-models/"
#Configs for all models (individual parameters will be set right before prediction)
mod_config = fconfig.HCD_CommonMod_Config()
mod_config.varmod = ["Oxidation[M]"]
mod_config.time_step = 100
mod_config.min_var_mod_num = 0
mod_config.max_var_mod_num = 3

def load_and_predict(modelfile, mod_config, peptides, nce, tmp_f, ion_types):
    model =  lstm.IonLSTM(mod_config)
    model.LoadModel(modelfile)
    start_time = time.perf_counter()
    if type(peptides) == list:
        buckets = load_data.load_peptides_as_buckets(peptides, mod_config, nce, instrument="unknown")
    else:
        buckets = load_data.load_peptide_file_as_buckets(peptides, mod_config, nce, instrument="unknown")
    read_time = time.perf_counter()
    output_buckets = model.Predict(buckets)
    predict_time = time.perf_counter()
    write_buckets_mgf(tmp_f.name, buckets, output_buckets, mod_config, iontypes = ion_types)
    print('read time = {:.3f}, predict time = {:.3f}'.format(read_time - start_time, predict_time - read_time))
    model.close_session()
    return flask.send_file(tmp_f.name)

@app.route("/")
def hello():
    return "Hello, I am pDeep2!\n"

@app.route("/<model>", methods=["POST"])
@app.route("/<model>/<fragmentation>", methods=["POST"])
@app.route("/<model>/<fragmentation>/<nl>", methods=["POST"])
def run_pDeep(model, fragmentation=None, nl=None):
    model= model.lower()
    if fragmentation:
        fragmentation = fragmentation.lower()
    if nl:
        nl = nl.lower()
    tmp_f = tempfile.NamedTemporaryFile(delete=True)
    @after_this_request
    def cleanup(response):
        tmp_f.close()
        return response
    if model == "tryptic":
        model_file = "model-180921-modloss/pretrain-180921-modloss.ckpt"
        nce = 0.35
    ###Adjust this part if you have other models available
    else:
        assert model =="nontryptic", "First Parameter must be either 'tryptic' or 'nontryptic'!"
        if fragmentation == 'cid':
            model_file = "CID_35/CID_35.ckpt"
            nce = 0.35
        else:
            assert fragmentation == "hcd", "Second Parameter must be either 'CID' or 'HCD'!"
            model_file = "HCD_25_27/HCD_25_27.ckpt"
            nce = 0.25
    ion_types = ['b{}', 'y{}', 'b{}-H2O', 'y{}-H2O', 'b{}-NH3', 'y{}-NH3'] if nl=="nl" else ['b{}', 'y{}']
    mod_config.SetIonTypes(ion_types)
    if flask.request.files:
        pDeep_input = flask.request.files["peptides"]
    else:
        #A single peptide
        assert all(param in flask.request.form for param in ['seq', 'charge']), "Syntax is 'seq=<sequence>&charge=<precursor_charge>[&mod=<modification_list>]"
        pDeep_input = ["{}\t{}\t{}".format(flask.request.form['seq'], flask.request.form['mod'] if 'mod' in flask.request.form else "", flask.request.form['charge']).split("\t")]
    return load_and_predict(model_folder + model_file, mod_config, pDeep_input, nce, tmp_f, ion_types)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p" "--port", action="store", dest="port")
    args = parser.parse_args()
    warnings.filterwarnings("ignore")

    app.run(host="0.0.0.0", port=args.port)
