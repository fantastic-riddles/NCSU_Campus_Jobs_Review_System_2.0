from app import db
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime


class Reviews(db.Model):
    """Model which stores the information of the reviews submitted"""
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(64), index=True, nullable=False)
    locations = db.Column(db.String(120), index=True, nullable=False)
    job_title = db.Column(db.String(64), index=True, nullable=False)
    job_description = db.Column(db.String(120), index=True, nullable=False)
    hourly_pay = db.Column(db.Integer, nullable=False)
    benefits = db.Column(db.String(120), index=True, nullable=False)
    review = db.Column(db.String(120), index=True, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    recommendation = db.Column(db.Integer, nullable=False)
    upvote_count = db.Column(db.Integer, default=0)


class Upvote(db.Model):
    """Model to track user upvotes on reviews"""
    id = db.Column(db.Integer, primary_key=True)
    review_id = db.Column(db.Integer, ForeignKey('reviews.id'), nullable=False)
    user_name = db.Column(db.String(10), ForeignKey('users.user_name'), nullable=False)

    # Ensure a user can upvote a review only once
    __table_args__ = (db.UniqueConstraint('review_id', 'user_name', name='_review_user_uc'),)
     
class User(db.Model):
    __tablename__ = 'users'
    user_name = db.Column(db.String(10), nullable=False, primary_key=True)
    name = db.Column(db.String(64),  index=True, nullable=False)
    email = db.Column(db.String(64), index=True, nullable=False)
    password = db.Column(db.String(24), index=True, nullable=False)
    type = db.Column(db.String(10), index=True, nullable=False)
    
    applications = relationship("Application", back_populates="user")
    jobs = relationship("Job", back_populates="employer") 
    experience = relationship("Experience", back_populates="user", uselist=False)

class Experience(db.Model):
    __tablename__ = 'experiences'
    id = db.Column(db.Integer, primary_key=True)
    cover_letter = db.Column(db.Text, nullable=True)
    prev_experience = db.Column(db.Text, nullable=True)
    linkedin_url = db.Column(db.String(255), nullable=True)  # Adding the LinkedIn URL field
    
    user_name = db.Column(db.String(10), ForeignKey('users.user_name'), unique=True)
    user = relationship("User", back_populates="experience")

class Job(db.Model):
    """Model that stores job details"""
    __tablename__ = 'jobs'
    job_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(164), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(164), nullable=False)
    pay = db.Column(db.Float, nullable=True)
    posted_date = db.Column(db.DateTime, default=datetime.utcnow)
    employer_id = db.Column(db.String(60), ForeignKey('users.user_name'), nullable=False)  # Reference to User table
    # Relationship to applications
    applications = relationship("Application", back_populates="job")
    employer = relationship("User", back_populates="jobs")  # Link to the employer
    

class Application(db.Model):
    __tablename__ = 'applications'
    application_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.Integer, ForeignKey('jobs.job_id'), nullable=False)
    user_name = db.Column(db.String(10), ForeignKey('users.user_name'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")