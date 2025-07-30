# Server Management

This is a Django-based server management application designed to help you track and manage your servers, hosts, virtual machines, and SSL certificates. It provides a user-friendly interface for managing server information, monitoring services, and keeping track of updates.

## Features

*   **Dashboard:** A central dashboard provides a quick overview of your servers, including counts of updates and services.
*   **Server Management:**
    *   Add, view, update, and delete servers.
    *   Track server details such as IP address, OS, CPU, memory, and disk space.
    *   Assign servers to departments and owners.
*   **Host and VM Management:**
    *   Manage hosts and their associated virtual machines.
    *   Track host details like hostname, IP address, and Hyper-V version.
    *   Add, view, update, and delete virtual machines.
*   **Service Monitoring:**
    *   Monitor services running on your servers.
    *   Track service status, port, and last restart time.
*   **Update Tracking:**
    *   Log server updates, including the type of update, notes, and attachments.
*   **SSL Certificate Tracking:**
    *   Monitor SSL certificates for your hyperlinks.
    *   Get notifications for expiring certificates.
*   **User and Department Management:**
    *   Manage users and departments.
    *   Role-based access control (Admin, Manager, Viewer).
*   **Hyperlink Management:**
    *   Manage hyperlinks associated with your servers.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/server-mgmt.git
    ```

2.  **Create a virtual environment and activate it:**

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
    ```

3.  **Install the dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration:**

    This project uses `.env` files for environment-specific configuration. There are three environments available: `local`, `dev`, and `prod`.

    *   **.env.example:** An example file with all the required environment variables.
    *   **.env:** Used for local development. Copy `.env.example` to `.env` and fill in the values.
    *   **.env.dev:** Used for the development server.
    *   **.env.prod:** Used for the production server.

    To use a specific environment, you can set the `ENVIRONMENT` variable in your shell, or the application will default to the `.env` file. For example, to run the development server with the `dev` environment settings, you would run:

    ```bash
    ENVIRONMENT=dev python manage.py runserver
    ```

    Or you can create a `.env` file from the example:
    ```bash
    cp .env.example .env
    ```
    And then update the variables in the `.env` file.


5.  **Run the database migrations:**

    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser:**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**

    ```bash
    python manage.py runserver
    ```

## Usage

1.  **Log in to the admin panel** at `http://127.0.0.1:8000/admin/` to manage users, groups, and departments.
2.  **Access the application** at `http://127.0.0.1:8000/` to view the dashboard and manage your servers.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you find a bug or have a feature request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
