// Manejar el envío del formulario de filtrado
document.getElementById('filter-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    fetchData(startDate, endDate);
});

// Función para obtener los datos de la API
function fetchData(startDate = '', endDate = '') {
    let apiUrl;

    // Detectar en qué página estás
    if (window.location.pathname === '/') {
        apiUrl = `/api/data?start_date=${startDate}&end_date=${endDate}`;  
    } else if (window.location.pathname === '/seguridad') {
        apiUrl = `/api/seguridad?start_date=${startDate}&end_date=${endDate}`;
    } else if (window.location.pathname === '/gobierno_mexico') {
        apiUrl = `/api/gobierno_mexico?start_date=${startDate}&end_date=${endDate}`;
    } else if (window.location.pathname === '/genero_opinion') {
        apiUrl = `/api/genero_opinion?start_date=${startDate}&end_date=${endDate}`;
    }

    // Hacer la petición fetch a la API correspondiente
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const tableBody = document.querySelector('#news-table tbody');
            tableBody.innerHTML = ''; 
            
            data.forEach(item => {
                const row = document.createElement('tr');
                
                const titleCell = document.createElement('td');
                titleCell.textContent = item.titulo;
                row.appendChild(titleCell);
                
                const summaryCell = document.createElement('td');
                summaryCell.textContent = item.descripcion;
                row.appendChild(summaryCell);
                
                const dateCell = document.createElement('td');
                dateCell.textContent = item.fecha;
                row.appendChild(dateCell);
                
                const linkCell = document.createElement('td');
                const link = document.createElement('a');
                link.href = item.link;
                link.target = '_blank';
                link.textContent = 'Ver más';
                linkCell.appendChild(link);
                row.appendChild(linkCell);
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

// Manejar el botón de scraping
document.getElementById('scrape-button').addEventListener('click', function() {
    let category;

    // Detectar en qué página estás
    if (window.location.pathname === '/') {
        category = 'informacion_relevante';
    } else if (window.location.pathname === '/seguridad') {
        category = 'seguridad';
    } else if (window.location.pathname === '/gobierno_mexico') {
        category = 'gobierno_mexico';
    } else if (window.location.pathname === '/genero_opinion') {
        category = 'genero_opinion';
    } else {
        console.error('Categoría no encontrada para esta página.');
        document.getElementById('result').innerHTML = 'Error: No se pudo determinar la categoría.';
        return;  
    }

    // Enviar la solicitud de scraping
    fetch('/scraping', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category: category })  
    })
    .then(response => response.json())
    .then(data => {
        const resultDiv = document.getElementById('result');
        if (data.status === 'success') {
            resultDiv.innerHTML = data.message; 
        } else {
            resultDiv.innerHTML = 'Error: ' + data.message;  
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = 'Error en la conexión con el servidor.';
    });
});

// Cargar datos inicialmente
fetchData();
