// TestMPI01.cpp : Este archivo contiene la función "main". La ejecución del programa comienza y termina ahí.
//

#include <iostream>
#include <mpi.h>
#include <vector>
#include <fstream>
#include <string>
#include "Dataset.h"

void generarVectorAletorio(std::vector<int>* vector);

int sumVector(const std::vector<int>& vec) {
    int sum = 0;
    for (int i : vec) {
        sum += i;
    }
    return sum;
}

std::vector<int> splitVector(std::vector<int> vector, int indexStart, int indexEnd) {

    std::vector<int> vectorSplitted = {};

    for (int i = indexStart; i < indexEnd; i++) {
        vectorSplitted.push_back(vector[i]);
    }

    return vectorSplitted;
}

int sumVectors(std::vector<int>& v1, std::vector<int>& v2) {
    int resultado = 0;
    for (int i = 0; i < v1.size(); i++) {
        resultado = resultado + (v1[i] + v2[i]);
    }

    return resultado;
}

std::vector<std::string> splitVector(std::string data, char delimitador) {
    std::vector<std::string> vectorResultante = {};
    std::string palabra = "";

    for (int i = 0; i < data.size(); i++) {
        if (data[i] == delimitador) {
            if(palabra != "") vectorResultante.push_back(palabra);
            palabra = "";
        }
        else {
            if (data[i] != *"\n" && data[i] != *"\t" && data[i] != *" " &&
                data[i] != *"c"  && data[i] != *"") {
                palabra = palabra + data[i];
            }
        }
    }

    if (palabra != "") vectorResultante.push_back(palabra);
    

    return vectorResultante;
}

std::vector<std::string> getHeader(Dataset *dataset, std::string data, char delimitador) {
    
    std::vector<std::string> vData = {};
    std::string text = "";
    
    Dataset dataCopia = *dataset;

    if (data[0] == *"c") vData = splitVector(data, delimitador);       

    if (!vData.empty()){
        Columna columna;
        columna.indice = 0;
        columna.nombre = vData[0];
        columna.tipoDato = vData[1];
        dataCopia.columna.push_back(columna);
    }

    return vData;
}

void getData(Dataset *dataset, std::string data, char delimitador) {
    std::vector<std::string> vData = {};
    std::string text = "";

    vData = splitVector(data, delimitador);
    for (int i = 0; i < vData.size(); i++) {

    }
}

int main(int argc, char** argv) {

    if (argc > 0) {
        std::cout << argv[1] << std::endl;
        std::fstream file;

        Dataset dataset;

        file.open(argv[1], std::ios::in);
        if (file.is_open()) {
            std::string result;
            std::string contenido;

            int linea = 0;

            std::vector<std::string> vData = {};
            while (std::getline(file, result)) {
                if (result[0] == *"c") {
                    std::vector<std::string> vDataTemp = {};
                    vDataTemp = getHeader(&dataset, result, *"\t");

                    for (int i = 0; i < vDataTemp.size(); i++) {
                        vData.push_back(vDataTemp[i]);
                    }
                }
                else {

                }
                contenido += result;
                linea++;
            }

            for (int i = 0; i < vData.size(); i++) {
                std::cout << i << ": " << vData[i] << " ";
            }
            std::cout << std::endl;
            file.close();
        }
    }

    MPI_Init(&argc, &argv);

    //Rank: Es el procesador que está ejecutando el proceso
    //Size: Número de procesadores específicados para la ejecución del proceso 
    int rank, size;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    std::vector<int> fvector (20);
    std::vector<int> svector (20);

    generarVectorAletorio(&fvector);
    generarVectorAletorio(&svector);

    int bloques = size;
    int buffer_size = fvector.size() / 3;

    std::cout << "Bloques: " << bloques << ", buffer: " << buffer_size << std::endl;

    //Primer procesador para gestión de datos, los demás operarán.
    if (rank == 0) {
        for (int i = 1; i < size; i++) {
            std::vector<int> vector(buffer_size);
            if (i == 1) vector = splitVector(fvector, 0, buffer_size);
            else vector = splitVector(fvector, buffer_size * (i - 1), buffer_size * i);

            MPI_Send(&vector[0], buffer_size, MPI_INT, i, 0, MPI_COMM_WORLD);
        }
    }
    
    if (rank > 0) {
        std::vector<int> vectorRecibir (buffer_size);
        MPI_Recv(&vectorRecibir[0], buffer_size, MPI_INT, 0, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

        std::cout << "Procesador " << rank << std::endl;
        int suma = 0;
        for (int i = 0; i < vectorRecibir.size(); i++) {
            std::cout << "Procesador " << rank << " " << vectorRecibir[i] << " ";
            suma = suma + vectorRecibir[i];
        }

        MPI_Send(&suma, 1, MPI_INT, 0, 0, MPI_COMM_WORLD);
    }

    if (rank == 0) {
        int resultado = 0; 
        for (int i = 1; i < size; i++) {
            int suma;
            MPI_Recv(&suma, 1, MPI_INT, i, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);

            resultado = resultado + suma;
        }

        std::cout << "R: " << resultado;
    }


    MPI_Finalize();
    return 0;
}

void generarVectorAletorio(std::vector<int> *vector) {
    for (int i = 0; i < (*vector).size(); i++) {
        (*vector)[i] = rand() % 100;
    }
}


