function fetchData() {
    let apiUrl;

    // Detectar en qué página estás usando 
    if (window.location.pathname === '/seguridad') {
        apiUrl = '/api/seguridad';
    } else if (window.location.pathname === '/genero_opinion') {
        apiUrl = '/api/genero_opinion';
    } else if (window.location.pathname === '/gobierno_mexico') {
        apiUrl = '/api/gobierno_mexico';
    } else {
        apiUrl = '/api/data';  
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

// Cargar datos inicialmente
fetchData();

// Actualizar datos cada 30 segundos
setInterval(fetchData, 30000);