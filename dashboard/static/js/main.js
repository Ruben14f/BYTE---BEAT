document.addEventListener("DOMContentLoaded", () => {
  // Configuración para cada gráfico
  const graficosConfig = [
    {
      id: "chart2",
      apiUrl: "/admin-dashboard/api/get-chart2/",
      filtroGlobalParam: "range",
      filtroIndParam: "range_chart2",
      filtroIndSelectId: "filtro-chart2",
      btnFiltrarIndId: "btn-filtrar-chart2",
      btnBorrarIndId: "btn-borrar-filtro-chart2",
    },
    {
      id: "chart3",
      apiUrl: "/admin-dashboard/api/get-chart3/",
      filtroGlobalParam: "range",
      filtroIndParam: "range_chart3",
      filtroIndSelectId: "filtro-chart3",
      btnFiltrarIndId: "btn-filtrar-chart3",
      btnBorrarIndId: "btn-borrar-filtro-chart3",
    },
    {
      id: "chart4",
      apiUrl: "/admin-dashboard/api/get-chart4/",
      filtroGlobalParam: "range",
      filtroIndParam: "range_chart4",
      filtroIndSelectId: "filtro-chart4",
      btnFiltrarIndId: "btn-filtrar-chart4",
      btnBorrarIndId: "btn-borrar-filtro-chart4",
    },
  ];

  // Instanciar gráficos y guardar referencias
  const graficos = {};
  graficosConfig.forEach(({ id }) => {
    const dom = document.getElementById(id);
    if (dom) {
      graficos[id] = echarts.init(dom);
    }
  });

  // Función genérica para cargar datos en un gráfico
  async function cargarGrafico(
    id,
    filtroGlobal = "",
    filtroIndividual = "",
    config
  ) {
    const chart = graficos[id];
    if (!chart) return;

    chart.showLoading();
    try {
      let url = config.apiUrl;
      const params = new URLSearchParams();

      // Prioriza filtro individual si existe
      if (filtroIndividual && config.filtroIndParam) {
        params.append(config.filtroIndParam, filtroIndividual);
      } else if (filtroGlobal && config.filtroGlobalParam) {
        params.append(config.filtroGlobalParam, filtroGlobal);
      }

      if (id === "chart4") {
      const topFilterSelect = document.getElementById("top_filter_chart4");
      if (topFilterSelect && topFilterSelect.value) {
        params.append("top_filter_chart4", topFilterSelect.value);
        }
      }

      if ([...params].length > 0) url += "?" + params.toString();

      const response = await fetch(url);
      const data = await response.json();

      chart.hideLoading();
      if (!data.series || data.series.length === 0) {
        chart.clear();
      }else {
        chart.clear();
        chart.setOption(data,true);
        chart.resize();
      }
    } catch (error) {
      chart.hideLoading();
      console.error(`Error loading ${id}:`, error);
    }
  }

  // Cargar todos los gráficos, pasando filtros global e individuales
  function cargarTodosGraficos(filtroGlobal = "") {
    graficosConfig.forEach((config) => {
      const filtroIndSelect = config.filtroIndSelectId
        ? document.getElementById(config.filtroIndSelectId)
        : null;
      const filtroIndValue = filtroIndSelect ? filtroIndSelect.value : "";
      cargarGrafico(config.id, filtroGlobal, filtroIndValue, config);
    });
  }

  // Control filtro global
  const filtroSelect = document.getElementById("filtro");
  const btnFiltrar = document.getElementById("btn-filtrar");
  const btnBorrarFiltro = document.getElementById("btn-borrar-filtro");

  btnBorrarFiltro.style.display = "none";

  btnFiltrar.addEventListener("click", () => {
    const filtro = filtroSelect.value || "";
    cargarTodosGraficos(filtro);
    btnBorrarFiltro.style.display = filtro ? "inline-block" : "none";

    
  });

  btnBorrarFiltro.addEventListener("click", () => {
    filtroSelect.value = "";
    btnBorrarFiltro.style.display = "none";
    cargarTodosGraficos("");
  });

  // Control filtros individuales (para cada gráfico que tenga filtro individual)
  graficosConfig.forEach((config) => {
    if (
      config.filtroIndSelectId &&
      config.btnFiltrarIndId &&
      config.btnBorrarIndId
    ) {
      const filtroIndSelect = document.getElementById(config.filtroIndSelectId);
      const btnFiltrarInd = document.getElementById(config.btnFiltrarIndId);
      const btnBorrarInd = document.getElementById(config.btnBorrarIndId);

      if (filtroIndSelect && btnFiltrarInd && btnBorrarInd) {
        btnBorrarInd.style.display = "none";

        btnFiltrarInd.addEventListener("click", () => {
          const filtroIndValue = filtroIndSelect.value || "";
          cargarGrafico(config.id, "", filtroIndValue, config);
          btnBorrarInd.style.display = filtroIndValue ? "inline-block" : "none";

          // Opcional: ocultar filtro global cuando hay filtro individual
          btnBorrarFiltro.style.display = "none";
          filtroSelect.value = "";
        });

        btnBorrarInd.addEventListener("click", () => {
          filtroIndSelect.value = "";
          btnBorrarInd.style.display = "none";
          cargarGrafico(config.id, "", "", config);
        });
      }
    }
  });

  // Carga inicial sin filtros
  cargarTodosGraficos("");
});
