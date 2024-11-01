# FlaskKeyring: A Secure Password Manager with Client-Side Encryption Powered by JavaScript and Python

<!--toc:start-->

-   [FlaskKeyring: A Secure Password Manager with Client-Side Encryption Powered by JavaScript and Python](#flaskkeyring-a-secure-password-manager-with-client-side-encryption-powered-by-javascript-and-python)
    -   [Introduction](#introduction)
    -   [Core Technologies](#core-technologies)
        -   [JavaScript and Client-Side Encryption](#javascript-and-client-side-encryption)
        -   [Python and Flask Backend](#python-and-flask-backend)
        -   [Full-Stack Development](#full-stack-development)
        -   [Database and ORM](#database-and-orm)
        -   [Security and Encryption](#security-and-encryption)
        -   [Email Capabilities](#email-capabilities)
    -   [Skills Demonstrated](#skills-demonstrated)
    -   [Deployment and Hosting](#deployment-and-hosting)
    -   [Features and Functionality](#features-and-functionality)
        -   [Client-Side Encryption with JavaScript](#client-side-encryption-with-javascript)
        -   [Python Backend Integration](#python-backend-integration)
        -   [Zero-Knowledge User Authentication](#zero-knowledge-user-authentication)
        -   [Advanced Password Management](#advanced-password-management)
        -   [Database Structure and Security](#database-structure-and-security)
        -   [Encryption and Security Details](#encryption-and-security-details)
        -   [Dynamic Templating and Modularity](#dynamic-templating-and-modularity)
    -   [Project Design and Structure](#project-design-and-structure)
    -   [Conclusion](#conclusion)
    -   [License](#license)
    <!--toc:end-->

## Introduction

FlaskKeyring, crafted solely by Andrea Arturo Venti Fuentes, is an advanced, full-stack password management solution that adheres to cutting-edge security principles, notably secure client-side encryption implemented with JavaScript. The application combines the power of JavaScript on the frontend and Python with Flask on the backend to provide a robust, intuitive, and highly secure platform for managing passwords. The project is deployed on Heroku and can be accessed at [flaskkeyring.com](https://www.flaskkeyring.com), demonstrating its scalability and readiness for production.

## Core Technologies

### JavaScript and Client-Side Encryption

-   **JavaScript**: Utilized on the client side to implement secure encryption and decryption of user passwords using the Web Cryptography API, ensuring that sensitive data is encrypted before being sent to the server.
-   **Web Cryptography API**: Provides robust cryptographic operations in the browser, allowing for client-side encryption using AES-GCM and key derivation with PBKDF2.

### Python and Flask Backend

-   **Python**: Powers the backend, handling server-side logic, integration of components, and management of database interactions.
-   **Flask**: Chosen for its balance between simplicity and flexibility, Flask serves as the web framework for handling server operations efficiently and scaling effectively.

### Full-Stack Development

-   **Frontend Excellence**: Built with HTML, CSS, JavaScript, and Bootstrap, FlaskKeyring offers a responsive, clean, and user-centric interface, prioritizing usability and user experience.
-   **Backend Integration**: The Python backend integrates various components, handles secure data processing, user authentication, and provides RESTful API endpoints for client-server communication.

### Database and ORM

-   **PostgreSQL & SQLAlchemy**: Provides robust and secure database management, with SQLAlchemy's ORM ensuring data integrity and seamless interactions between the application and the database.
-   **SQLite**: Employed for local testing to streamline feature development and testing workflows.

### Security and Encryption

-   **Zero-Knowledge Security Model**: Implements client-side encryption using JavaScript, ensuring that even if the database is compromised, no plaintext passwords can be decrypted without the user's master password.
-   **Advanced Cryptographic Techniques**: Utilizes AES-GCM encryption and PBKDF2 key derivation via the Web Cryptography API in JavaScript. The encryption keys are derived client-side from a master password that is never sent to the server, meaning password data remains inaccessible without the client-side key.

### Email Capabilities

-   **Flask-Mail Integration**: Facilitates automated, secure email notifications for account verification and password reset requests, enhancing user experience and security.

## Skills Demonstrated

-   **Languages**: JavaScript, Python, HTML, CSS
-   **Frontend Development**: Advanced JavaScript for client-side encryption, responsive design, dynamic templating with Jinja2.
-   **Backend Development**: Python, Flask, RESTful API design, session management with Flask-Login and Flask-Session, email integration with Flask-Mail.
-   **Encryption & Security**: Implemented client-side encryption using JavaScript and the Web Cryptography API, AES-GCM, PBKDF2, zero-knowledge security model.
-   **Database & ORM**: PostgreSQL, SQLAlchemy, SQLite3
-   **Deployment & Hosting**: Heroku, version control with Git
-   **Project Management**: Modular code organization, scalability, maintainability, security-first design principles.

## Deployment and Hosting

-   **Heroku**: Chosen for its scalable, cloud-based deployment capabilities, allowing FlaskKeyring to function efficiently in a production environment with seamless scalability.

## Features and Functionality

### Client-Side Encryption with JavaScript

-   **Secure Encryption in the Browser**: JavaScript, along with the Web Cryptography API, is used to encrypt passwords on the client side before any data is transmitted to the server.
-   **Master Password Handling**: The master password is used to derive encryption keys client-side and is never sent to the server, ensuring a zero-knowledge approach.

### Python Backend Integration

-   **Data Handling and API**: The Python backend handles data storage, user authentication, and provides RESTful API endpoints for the client to interact with securely.
-   **Database Interactions**: Manages all database interactions, ensuring data integrity and security.

### Zero-Knowledge User Authentication

-   **Complete Authentication System**: Secure registration, login, and password reset functionalities integrated with email verification for account security.
-   **Client-Side Encryption for Passwords**: Passwords are encrypted client-side using JavaScript before transmission to the server, where only encrypted data is stored.

### Advanced Password Management

-   **Secure Storage of Encrypted Data**: Encrypts passwords, IV, and salt client-side to ensure that only ciphertext is stored on the server.
-   **User-Friendly Interface**: Provides a seamless experience for adding, editing, and deleting passwords with real-time updates and visual feedback.
-   **Password Generation and Search**: Implements secure password generation and efficient search functionalities to streamline user experience.

### Database Structure and Security

-   **User Data Integrity**: Contains structured tables including `users`, `passwords`, `reset_tokens`, and `folders` to organize and protect sensitive information.
-   **Only Encrypted Data Stored**: Ensures compliance with best practices for zero-knowledge encryption by storing only ciphertext and decryption parameters (`iv` and `salt`).

### Encryption and Security Details

-   **Client-Side AES-GCM Encryption**: Using JavaScript and the Web Cryptography API, passwords are encrypted on the client side before reaching the server.
-   **Password Derivation Using PBKDF2**: Derives encryption keys client-side from a master password and a unique salt, reinforcing a zero-knowledge approach where decryption requires the master password, which is never stored or transmitted.

### Dynamic Templating and Modularity

-   **Jinja2 Integration**: Templates are dynamically rendered for seamless navigation and an interactive user experience, from `dashboard.html` to `view_passwords.html`.
-   **Flask Blueprints**: Modular structure organizes routes into logical sections, following best practices in Flask for maintainability and scalability.

## Project Design and Structure

-   **Client-Side Encryption with JavaScript**: Demonstrates expertise in JavaScript by implementing secure client-side encryption, leveraging the Web Cryptography API for cryptographic operations.
-   **Python Backend for Integration**: The backend, built with Python and Flask, integrates all components, manages user sessions, handles database interactions, and provides secure APIs.
-   **Modular and Maintainable Code**: Organized with separate modules for models, views, and utilities, enhancing code readability and scalability.
-   **Security-First Development**: Designed with a strong focus on security, implementing client-side encryption, secure session management, and email verification to protect user data.

## Conclusion

FlaskKeyring is a comprehensive password management solution that leverages both JavaScript and Python to provide a secure, user-friendly application with client-side encryption. By implementing encryption directly in the browser using JavaScript, and managing backend processes with Python and Flask, the application ensures that user data remains confidential and secure. Every detail, from frontend encryption logic to backend integration, reflects a sophisticated understanding of full-stack development and cybersecurity principles. FlaskKeyring exemplifies a robust, scalable, and secure solution built for real-world application, underscoring my full-stack development skills and commitment to secure, user-friendly applications.

## License

The application is licensed under the [FlaskKeyring License Agreement](LICENSE), restricting its use to Heroku and prohibiting local installation or distribution.
