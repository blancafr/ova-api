from models.paciente import PacienteCreate
from datetime import datetime
from .models import Paciente

def insertar_paciente(db, paciente: PacienteCreate):
    print(f"{datetime.now().isoformat()}: Paciente recibido: {paciente}")
    
    db_paciente = Paciente(
        sexo=paciente.sexo,
        edad=paciente.edad,
        comentario=paciente.comentario,
        enfermedad=paciente.enfermedad,
        fecha_registro=paciente.fecha
    )
    
    db.add(db_paciente)
    db.commit()
    db.refresh(db_paciente)
    
    return db_paciente