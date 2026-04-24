# GIKI Load Shedding Scheduler and Feeder Management System

## Short Description
This project is a Python OOP-based simulation of a fair and priority-based load shedding system for the GIKI campus. It models academic, residential, and utility buildings as power units and generates ON/OFF feeder schedules according to available supply and selected time slots.

## UML Class Diagram

![UML Class Diagram](screenshots/uml_diagram.png)

## Project Objective
The main objective of this project is to simulate how load shedding decisions can be automated in a structured and fair way using object-oriented programming. The system is designed to protect important campus buildings according to their type and timing while demonstrating core OOP concepts in a real-world electrical engineering context.

## Features
- Priority-based load shedding
- Time-slot based feeder scheduling
- Fair rotation using outage count
- Separate handling of academic, residential, and utility buildings
- Total demand calculation against available supply
- ON/OFF status generation with reasons
- Input validation and exception handling
- Simple Tkinter GUI for user interaction

## OOP Concepts Used
- **Encapsulation**  
  Private and protected attributes are used for load, outage count, and category, with controlled access through methods.

- **Inheritance**  
  `AcademicBuilding`, `ResidentialBuilding`, and `UtilityBuilding` inherit from the parent class `PowerUnit`.

- **Polymorphism**  
  The `get_priority(time_slot)` method is overridden in child classes to assign different priorities based on building type and time slot.

- **Modular and Scalable Design**  
  The project is divided into multiple classes, each with a clear responsibility such as building representation, scheduling, record storage, and GUI handling.

## Technologies Used
- Python 3
- Tkinter
- Object-Oriented Programming (OOP)

## How to Run the Project
1. Install Python 3 on your system.
2. Download or clone this repository.
3. Open the project folder.
4. Run the Python file:

```bash
Load Shedding Schedule Python File.py
