// Manejar el envío del formulario de filtrado
document.getElementById('filter-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    const source = document.getElementById('source-select').value;

    fetchData(startDate, endDate, source);
});

// Función para obtener los datos de la API
function fetchData(startDate = '', endDate = '', source= '') {
    let apiUrl;

    // Detectar en qué página estás
    switch (window.location.pathname) {
        case '/':
            apiUrl = `/api/data?start_date=${startDate}&end_date=${endDate}&source=${source}`;  
            break;
        case '/seguridad':
            apiUrl = `/api/seguridad?start_date=${startDate}&end_date=${endDate}&source=${source}`;
            break;
        case '/gobierno_mexico':
            apiUrl = `/api/gobierno_mexico?start_date=${startDate}&end_date=${endDate}&source=${source}`;
            break;
        case '/genero_opinion':
            apiUrl = `/api/genero_opinion?start_date=${startDate}&end_date=${endDate}&source=${source}`;
            break;
        default:
            console.error('Ruta no válida');
            return;
    }

    // Hacer la petición fetch a la API correspondiente
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta de la API');
            }
            return response.json();
        })
        .then(data => {
            const tableBody = document.querySelector('#news-table tbody');
            tableBody.innerHTML = ''; 
            
            data.forEach(item => {
                const row = document.createElement('tr');
                
                //Titulo
                const titleCell = document.createElement('td');
                titleCell.textContent = item.titulo;
                row.appendChild(titleCell);
                
                //Resumen
                const summaryCell = document.createElement('td');
                summaryCell.textContent = item.descripcion;
                row.appendChild(summaryCell);
                
                //Fecha
                const dateCell = document.createElement('td');
                dateCell.textContent = item.fecha;
                row.appendChild(dateCell);
                
                //Link
                const linkCell = document.createElement('td');
                const link = document.createElement('a');
                link.href = item.link;
                link.target = '_blank';
                link.textContent = 'Ver más';
                linkCell.appendChild(link);
                row.appendChild(linkCell);

                // Fuente
                const sourceCell = document.createElement('td');
                const img = document.createElement('img');
                img.src = item.fuente; 
                img.alt = 'Logo';
                img.className = 'source-logo'; 
                sourceCell.appendChild(img); 
                row.appendChild(sourceCell); 
                
                tableBody.appendChild(row);
            });
        })
        .catch(error => console.error('Error al cargar los datos:', error));
}

// Función para ocultar el resultado después de un retraso
function hideResultAfterDelay() {
    setTimeout(() => {
        document.getElementById('result').innerHTML = ''; 
        document.getElementById('result').style.display = 'none'; 
    }, 10000); 
}

// Manejar el botón de scraping
document.getElementById('scrape-button').addEventListener('click', function() {
    // Limpiar el área de resultados
    document.getElementById('result').innerHTML = ''; 
    document.getElementById('result').style.display = 'none'; 

    let category;

    // Detectar en qué página estás
    switch (window.location.pathname) {
        case '/':
            category = 'informacion_relevante';
            break;
        case '/seguridad':
            category = 'seguridad';
            break;
        case '/gobierno_mexico':
            category = 'gobierno_mexico';
            break;
        case '/genero_opinion':
            category = 'genero_opinion';
            break;
        default:
            console.error('Categoría no encontrada para esta página.');
            document.getElementById('result').innerHTML = 'Error: No se pudo determinar la categoría.';
            document.getElementById('result').style.display = 'block'; 
            hideResultAfterDelay(); 
            return;  
    }

    // Mostrar la barra de carga
    const loader = document.createElement('div');
    loader.className = 'loader';
    loader.innerHTML = `
        <div class="loading-text">
            Cargando<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
        </div>
        <div class="loading-bar-background">
            <div class="loading-bar" id="loading-bar" style="width: 0%;"></div>
        </div>
    `;
    document.getElementById('result').appendChild(loader);
    document.getElementById('result').style.display = 'block'; 

    // Enviar la solicitud de scraping
    fetch('/scraping', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ category: category })  
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Error en la respuesta del scraping');
        }
        return response.json();
    })
    .then(data => {
        const loadingBar = document.getElementById('loading-bar');

        if (data.status === 'success') {
            loadingBar.style.width = '100%';  
            loadingBar.innerText = 'Completado';
            document.getElementById('result').innerHTML = data.message; 
        } else {
            loadingBar.style.width = '100%';  
            loadingBar.innerText = 'Error';
            document.getElementById('result').innerHTML = 'Error: ' + data.message;  
        }

        // Llamar a la función para ocultar el resultado 
        hideResultAfterDelay();
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').innerHTML = 'Error en la conexión con el servidor.';
        const loadingBar = document.getElementById('loading-bar');
        loadingBar.style.width = '100%';  
        loadingBar.innerText = 'Error';

        // Llamar a la función para ocultar el resultado
        hideResultAfterDelay();
    });
});

// Cargar datos inicialmente
fetchData();
