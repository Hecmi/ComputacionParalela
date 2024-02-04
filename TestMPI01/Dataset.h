#ifndef DATASET_H
#define DATASET_H

#include <vector>
#include <string>

struct Columna;

struct Dataset
{
	std::vector<Columna> columna;

	std::vector<int> valorE;
	std::vector<std::string> valorS;
	std::vector<double> valorD;
};

struct Columna {
	int indice;
	std::string nombre;
	std::string tipoDato;
};

#endif