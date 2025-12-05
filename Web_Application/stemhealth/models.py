from stemhealth import db

# Batch model: Represents a batch of seedlings
class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    species = db.Column(db.String(100), nullable=False)
    optimum_duration = db.Column(db.String(50), default=None)
    optimum_entry_id = db.Column(db.Integer, default=None)
    entries = db.relationship('Entry', backref='batch', lazy=True)
    
    def __repr__(self):
        return f"Batch('{self.name}', '{self.species}')"

# Entry model: Represents a single entry of a batch
class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_image_filepath = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    humidity = db.Column(db.Float, nullable=False)
    predicted_image_filepath = db.Column(db.String(100), default=None)
    predicted_seedlings = db.Column(db.Integer, default=0)
    average_height = db.Column(db.Float, server_default="0.0")
    individual_heights = db.relationship('IndividualHeight', backref='entry', lazy=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batch.id'), nullable=False)

    def __repr__(self):
        return f"Entry('{self.original_image_filepath}', '{self.timestamp}', '{self.temperature}', '{self.humidity}')"
    
# IndividualHeight model: Represents the height of a single seedling and its associated YOLO prediction data
class IndividualHeight(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    height = db.Column(db.Float, nullable=False)
    label = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    x1 = db.Column(db.Integer, nullable=False)
    y1 = db.Column(db.Integer, nullable=False)
    x2 = db.Column(db.Integer, nullable=False)
    y2 = db.Column(db.Integer, nullable=False)
    entry_id = db.Column(db.Integer, db.ForeignKey('entry.id'), nullable=False)

    def __repr__(self):
        return f"IndividualHeight('{self.height}', '{self.yolo_prediction})"
    
    def to_dict(self):
        return {
            'id': self.id,
            'height': self.height,
            'label': self.label,
            'confidence': self.confidence,
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'entry_id': self.entry_id
        }
