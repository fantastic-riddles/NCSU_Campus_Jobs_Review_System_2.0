-- SQLite

-- Insert dummy data into jobs table
INSERT INTO jobs (title, description, location, posted_date, pay, employer_id)
VALUES 
    ('Software Engineer', 'Develop and maintain web applications.', 'San Francisco, CA', '2024-01-10 09:00:00', 120000.00, 'employer1'),
    ('Data Analyst', 'Analyze data trends and generate reports.', 'New York, NY', '2024-02-15 10:30:00', 70000.00, 'employer2'),
    ('Marketing Specialist', 'Create and implement marketing strategies.', 'Austin, TX', '2024-03-20 11:15:00', 60000.00, 'employer3'),
    ('Project Manager', 'Oversee project timelines and deliverables.', 'Remote', '2024-04-05 13:45:00', 90000.00, 'employer1'),
    ('UX Designer', 'Design user interfaces for mobile applications.', 'Seattle, WA', '2024-05-12 08:20:00', 85000.00, 'employer4'),
    ('Frontend Developer', 'Develop responsive web frontends using React.', 'Los Angeles, CA', '2024-06-25 14:30:00', 95000.00, 'employer2'),
    ('Backend Developer', 'Implement backend services and APIs.', 'Chicago, IL', '2024-07-18 09:50:00', 100000.00, 'employer3'),
    ('Business Analyst', 'Conduct business analysis and process improvement.', 'Boston, MA', '2024-08-21 12:00:00', 75000.00, 'employer4');
