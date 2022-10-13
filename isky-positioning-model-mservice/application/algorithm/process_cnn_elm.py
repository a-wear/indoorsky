#!/usr/bin/python
from knn_positioning import Position_KNN
from data_partition import data_partition
from elm import elmTrain_fix, elmPredict_optim
from cnn import convlayer
from appwrite.exception import AppwriteException
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.input_file import InputFile
from appwrite.query import Query
from appwrite.services.storage import Storage
from appwrite.input_file import InputFile

import keras.backend as K

import numpy as np
from flask import jsonify
from dotenv import load_dotenv
from io import BytesIO
import re
import joblib
import argparse
import uuid
import json
import os

dotenv_path = os.path.join(os.getcwd(), '.env')

if os.path.exists(dotenv_path):
   load_dotenv(dotenv_path)


client = Client()
client.set_endpoint(os.environ['APPWRITEENDPOINT'])
client.set_project(os.environ['APPWRITEPROJECTID'])
client.set_key(os.environ['APPWRITEAPIKEY'])

database_id = os.environ['RDB_DB']
config_preproc_id = os.environ['TABLE_PREPROCESSING']
bucket_model_id = os.environ['TABLE_FILE']
bucket_preprocessing_id=os.environ['TABLE_FILE_PREPROCESSING']
dataset_id = os.environ['TABLE_DATASET']
data_model = os.environ['TABLE_MODEL']


def get_dataset(dataset: str):
    try:
        databases = Databases(client=client)
        documents = databases.get_document(database_id, dataset_id, dataset)
        data = json.dumps(documents)
        return str(data)
    except AppwriteException as e:
        print({'code': '0', 'message': e.message})


def get_data_preprocessed_by_id(conf_prepro_id: str):
        try:
            databases = Databases(client)
            documents = databases.list_documents(database_id, config_preproc_id,
                                              queries=[Query.equal('id_preprocessing', conf_prepro_id)])
            data = {}
            if documents['total'] != 0:
                for document in documents['documents']:
                    data[document['parameter']] = document['value']
                
                return json.dumps(data)
                
            return jsonify({'code':404, 'message': 'File not found.'})
        except AppwriteException as e:
            return jsonify({'code':501, 'message': e.message})


def upload_file(file_path:str) -> str:
    try:
        storage = Storage(client)
        response = storage.create_file(bucket_id=bucket_model_id, file_id='unique()', file=InputFile.from_path(file_path))
        return response['$id']
    except AppwriteException as e:
        print({'code': '0', 'message': e.message})


def insert_document(collection_id: str, data: dict) -> str:
    try:
        databases = Databases(client)
        response = databases.create_document(database_id=database_id, collection_id=collection_id, 
                                             document_id='unique()', data=data)
        return response['$id']
    except AppwriteException as e:
        print({'code': '0', 'message': e.message})
      
        
def insert_data(collection_id: str, id:str, parameter: str, value: str, path_file: str):
    
    if path_file != "":
        file_id = upload_file(path_file)
        value = file_id
           
    data = {
        "id_model": id,
        "parameter": parameter,
        "value": value
        }
        
    insert_document(collection_id=collection_id, data=data)



if __name__ == '__main__':
    p = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description='')
    p.add_argument('--params', dest='params', action='store', default='', help='Arguments')
    
    args = p.parse_args()

    params = json.loads(args.params)
    
    # Create a temporal directory to store files
    temp_path = os.path.join(os.getcwd(), 'application', 'temp')
    
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    # Unique ID for all files generated
    uuid_file = str(uuid.uuid1())
    
    # Save parameters
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='name', value=params['name'], 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='dataset_id', value=params['dataset_id'], 
                path_file='')
    # CNN data
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.padding', value=str(params['cnn']['padding']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.strides', value=str(params['cnn']['strides']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.data_format', value=str(params['cnn']['data_format']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.act_funct', value=str(params['cnn']['act_funct']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.kernel_size', value=str(params['cnn']['kernel_size']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='cnn.filter', value=str(params['cnn']['filter']), 
                path_file='')
    # ELM model data
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.act_funct', value=str(params['elm']['act_funct']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.c', value=str(params['elm']['c']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.hidden_neurons', value=str(params['elm']['hidden_neurons']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.weight_intialization', value=str(params['elm']['weight_intialization']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.weight_initializatio_bits', value=str(params['elm']['weight_initializatio_bits']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='elm.output_weits_bits', value=str(params['elm']['output_weits_bits']), 
                path_file='')
    
    # Test data
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='test.percent_test', value=str(params['test']['percent_test']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='test.test_accuracy', value=str(params['test']['test_accuracy']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='test.k', value=str(params['test']['k']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='test.distance_metric', value=str(params['test']['distance_metric']), 
                path_file='')
    
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='is_active', value=str(params['is_active']), 
                path_file='')
    insert_data(collection_id=data_model, id=uuid_file, 
                parameter='created_at', value=str(params['created_at']), 
                path_file='')
    
    # Get dataset
    dataset_data = json.loads(get_dataset(dataset=params['dataset_id']))    
    data_preprocessing = get_data_preprocessed_by_id(dataset_data['process_id'])
    
    data_preprocessing_to_json = json.loads(data_preprocessing)
    
    # Create a temporal directory to store files
    temp_path = os.path.join(os.getcwd(), 'application', 'temp')
    
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    
    storage = Storage(client)
    
    file = {}
    
    # Save files in the terporal dir 
    for key, value in data_preprocessing_to_json.items():
        parameter = key.split('_')
        if  parameter[-1] == 'file':
            load_file = storage.get_file_view(bucket_preprocessing_id, value)
            file_tranform = BytesIO(load_file)
            file[key] = joblib.load(file_tranform)
            
    if dataset_data['technique'] == 'NORMALIZATION':
        x_train_preprocessed = file['x_data_normalization_file']
    elif dataset_data['technique'] == 'TRANSFORMATION':
        x_train_preprocessed = file['x_data_transformed_file']
    else:
        x_train_preprocessed = file['x_data_original_file']
            
    y_train = file['y_data_original_file'].copy()
    # Rename columns
    y_train.columns = ['LONGITUDE','LATITUDE','ALTITUDE','FLOOR','BUILDINGID']
    
    y_train_temp = y_train.copy()
    
    # Label encoding floor
    encoding = file['floor_label_encoder_file']
    lab_encoded_floor = encoding.transform(y_train['FLOOR']).reshape(-1, 1)
    
    y_train_temp['FLOOR'] = lab_encoded_floor
    
    # Label encoding building
    encoding_building = file['building_label_encoder_file']
    lab_encoded_building = encoding_building.transform(y_train['BUILDINGID'])
    
    y_train_temp['BUILDINGID'] = lab_encoded_floor
    
    X_train = x_train_preprocessed
    
    
    # Test data cleansed
    if params['test']['test_accuracy']== True:
        X_new_train,  y_new_train, X_new_validation, y_new_validation= data_partition(X_train=X_train, y_train=y_train_temp,
                                                                                      test_data_percent=params['test']['percent_test'])
        
        # Data reshape
        x_train = X_train.reshape((X_train.shape[0], X_train.shape[1], 1))
        X_test = X_new_validation.values.reshape((X_new_validation.shape[0], X_new_validation.shape[1], 1))
        
        # Training Models
        # General
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')

        intrain = K.variable(x_train)
        intest = K.variable(x_test)

        # CNN Model
        t1 = ti.time()
        out_train_ = convlayer(intrain, cnn_config=cnn_config)
        out_test_ = convlayer(intest, cnn_config=cnn_config)

        # Effective computation of the input preprocessing flow

        out_train = K.eval(out_train_)
        out_test = K.eval(out_test_)
        ttrain_cnn = ti.time()-t1
        K.clear_session()  # to avoid overloads

        # ELM
        Samples = out_train.T
        Labels_floor = y_train_floor_oe
        Labels_bld = y_train_build_oe

        # ELM - training
        t1 = ti.time()
        inW, outW, h_train = elmTrain_fix(Samples, np.transpose(Labels_floor), elm_config["hidden_neurons"],
                                        elm_config["C"], elm_config["act_funct"], elm_config["win_bits"])

        inW_bld, outW_bld, h_train_bld = elmTrain_fix(Samples, np.transpose(Labels_bld), elm_config["hidden_neurons"],
                                        elm_config["C"], elm_config["act_funct"], elm_config["win_bits"])
        ttrain = ti.time() - t1 + ttrain_cnn

        print(" training time: %f seconds" % ttrain)
        # ==============  Quantify the output layer ======================================
        Qout = -1 + pow(2, elm_config["wout_bits"] - 1)
        if elm_config["wout_bits"] > 0:
            O = np.max(np.abs(outW))
            outW = np.round(outW * (1 / O) * Qout)

            O_bld = np.max(np.abs(outW_bld))
            outW_bld = np.round(outW_bld * (1 / O_bld) * Qout)

        # ================= TEST (VALIDATION) DATASET LOADING

        SamplesTest = out_test.T

        # ====================== VALIDATION PHASE (+ Accuracy evaluation) =================
        t2 = ti.time()
        scores, h_test = elmPredict_optim(SamplesTest, inW, outW, elm_config["act_funct"])
        scores_bld, h_test_bld = elmPredict_optim(SamplesTest, inW_bld, outW_bld, elm_config["act_funct"])

        ttest = ti.time() - t2
        print(" prediction time: %f seconds" % ttest)

        # Floor prediction
        round_predictions = np.argmax(np.transpose(scores), axis=-1)
        cm = confusion_matrix(y_true=y_test_floor, y_pred=round_predictions)
        accuracy = (np.trace(cm) / float(np.sum(cm))) * 100

        # Building
        round_predictions_bld = np.argmax(np.transpose(scores_bld), axis=-1)
        cm_bld = confusion_matrix(y_true=y_test_bld, y_pred=round_predictions_bld)
        accuracy_bld = (np.trace(cm_bld) / float(np.sum(cm_bld))) * 100

        labels = np.unique(y_train_floor)
        
        position = Position_KNN(k=params['test']['k'], metric=params['test']['distance_metric'])
        position.fit(X_new_train, y_new_train.values)
        floor_hit_rate_org, true_false_values_org, pred_fhr_org = position.floor_hit_rate(X_new_validation, y_new_validation.values)
        building_hit_rate_org, pred_bhr_org = position.building_hit_rate(X_new_validation, y_new_validation.values)
        error2D_org, error2D_values_org = position.predict_position_2D(X_new_validation, y_new_validation.values, true_floors=true_false_values_org)
        error3D_org, error3D_values_org = position.predict_position_3D(X_new_validation, y_new_validation.values)
        
        insert_data(collection_id=data_model, id=uuid_file, 
                    parameter='result.mean_3d_error', value=str(round(error3D_org, 2)), 
                    path_file='')
        insert_data(collection_id=data_model, id=uuid_file, 
                    parameter='result.mean_2d_error', value=str(round(error2D_org, 2)), 
                    path_file='')
        insert_data(collection_id=data_model, id=uuid_file, 
                    parameter='result.building_hit_rate', value=str(round(building_hit_rate_org, 2)), 
                    path_file='')
        insert_data(collection_id=data_model, id=uuid_file, 
                    parameter='result.floor_hit_rate', value=str(round(floor_hit_rate_org, 2)), 
                    path_file='')
        
        