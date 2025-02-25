#################################################################
# Convertir archivos en formato MARCXML a EPrintsXML
#################################################################

import xml.etree.ElementTree as ET
from pymarc import MARCReader
import datetime

class MarcToEprintsConverter:
    def __init__(self):
        # Namespace para ePrints
        self.eprints_ns = "http://www.loc.gov/MARC21/slim"
        self.ns = {"marc": self.eprints_ns}

    def convert_file(self, marcxml_file, output_file):
        """Convierte un archivo MARCXML a ePrints XML"""
        try:
            # Parsear el archivo MARCXML
            tree = ET.parse(marcxml_file)
            root = tree.getroot()

            # Crear el documento ePrints
            eprints_root = ET.Element("eprints")
            #            eprint = ET.SubElement(eprints_root, "eprint")

            # Procesar cada registro MARC
            for record in root.findall(".//marc:record", self.ns):
                eprint = ET.SubElement(eprints_root, "eprint")
                self.process_record(record, eprint)

            # Guardar el resultado
            tree = ET.ElementTree(eprints_root)
            tree.write(
                output_file,
                encoding="utf-8",
                xml_declaration=True,
            )
            return True

        except Exception as e:
            print(f"Error durante la conversión: {str(e)}")
            return False

    def process_record(self, record, eprint):
        """Procesa un registro MARC y lo convierte a elementos ePrints"""

        # Mapeo básico de campos MARC a ePrints
        field_mapping = {
            "245": self.process_title,  # Título
            "100": self.process_author,  # Autor
            "264": self.process_publication,  # Publicación
#            "245": self.process_abstract,  # Resumen
            "653": self.process_subjects,  # Temas
        }

        # Procesar cada campo de datos
        for datafield in record.findall(".//marc:datafield", self.ns):
            tag = datafield.get("tag")
            if tag in field_mapping:
                field_mapping[tag](datafield, eprint)

    def process_title(self, datafield, eprint):
        """Procesa el título (245)"""
        title = datafield.find(".//marc:subfield[@code='a']", self.ns)
        title_resto = datafield.find(".//marc:subfield[@code='b']", self.ns)
        title_mencion = datafield.find(".//marc:subfield[@code='c']", self.ns)
        if title is not None and title.text:
            title_elem = ET.SubElement(eprint, "title")
            title_elem.text = title.text.strip()+"\n"
        if title_resto is not None and title_resto.text:
            title_elem.text = title_elem.text + title_resto.text.strip()+"\n"
        if title_mencion is not None and title_mencion.text:
            title_elem.text = title_elem.text + title_mencion.text.strip() + "\n"

    def process_author(self, datafield, eprint):
        """Procesa el autor (100)"""
        author = datafield.find(".//marc:subfield[@code='a']", self.ns)
        if author is not None and author.text:
            creators = ET.SubElement(eprint, "creators")
            creator = ET.SubElement(creators, "item")
            name = ET.SubElement(creator, "name")
            family = ET.SubElement(name, "family")
            given = ET.SubElement(name, "given")
            # Dividir nombre (esto es una simplificación)
            author_name = author.text.strip().split(",")
            family.text = author_name[0] if author_name else ""
            given.text = author_name[1] if len(author_name) > 1 else ""

    def process_publication(self, datafield, eprint):
        """Procesa la información de publicación (264)"""
        publisher = datafield.find(".//marc:subfield[@code='b']", self.ns)
        date = datafield.find(".//marc:subfield[@code='c']", self.ns)

        if publisher is not None and publisher.text:
            pub_elem = ET.SubElement(eprint, "publisher")
            pub_elem.text = publisher.text.strip()+"\n"

        if date is not None and date.text:
            date_elem = ET.SubElement(eprint, "date")
            date_elem.text = date.text.strip()+"\n"

    def process_abstract(self, datafield, eprint):
        """Procesa el resumen (245)"""
        abstract = datafield.find(".//marc:subfield[@code='a']", self.ns)
        abs_1 = datafield.find(".//marc:subfield[@code='b']", self.ns)
        abs_2 = datafield.find(".//marc:subfield[@code='c']", self.ns)
        if abstract is not None and abstract.text:
            abs_elem = ET.SubElement(eprint, "abstract")
            abs_elem.text = abstract.text.strip()+"\n"
        if abs_1 is not None and abs_1.text:
            abs_elem.text = abs_elem.text+abs_1.text.strip()+"\n"
        if abs_2 is not None and abs_2.text:
            abs_elem.text = abs_elem.text + abs_2.text.strip() + "\n"

    def process_subjects(self, datafield, eprint):
        """Procesa los temas (653)"""
        subject = datafield.find(".//marc:subfield[@code='a']", self.ns)
        if subject is not None and subject.text:
            subjects = ET.SubElement(eprint, "subjects")
            item = ET.SubElement(subjects, "item")
            item.text = subject.text.strip()+"\n"


# Ejemplo de uso
def main():
    converter = MarcToEprintsConverter()

    # Archivos de entrada y salida
    input_file = "tesis.xml"
    output_file = "output_eprints.xml"

    print(f"Convirtiendo {input_file} a {output_file}...")
    success = converter.convert_file(input_file, output_file)

    if success:
        print("Conversión completada exitosamente")
    else:
        print("Falló la conversión")


if __name__ == "__main__":
    # Instalar pymarc primero: pip install pymarc
    main()
