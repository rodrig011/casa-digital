// Demostraciones en línea de un cliente (clientiatech.com/demos/...): la página corre el bot real en el navegador,
// con el archivo del negocio y estos datos de prueba en lugar de los privados (números y cuenta de ejemplo).
// El servidor de la demo (demo.js) usa lo mismo para armarle a Claude el mismo sistema y herramientas.
const { cargarNegocio } = require("./negocio");

const DEMOS = {
  "con-sabor-a-pueblo": {
    archivo: "negocios/con-sabor-a-pueblo.json",
    privado: {
      sucursales: { tegucigalpa: { whatsapp: "+504 0000-0003" }, sps: { whatsapp: "+504 0000-0003" } },
      repartidores: [{ id: "kevin", nombre: "Kevin", whatsapp: "+504 0000-0001", sucursal: "sps" }, { id: "tegusgo", nombre: "Tegusgo", whatsapp: "+504 0000-0002", sucursal: "tegucigalpa" }],
      cobro: { transferencia: "Banco de ejemplo, cuenta 000-000000-0 (dato de prueba)" },
      proveedores: [
        { id: "cerdo", nombre: "Granja (ejemplo)", producto: "Cerdo en canal", whatsapp: "+504 0000-0010" },
        { id: "tortillas-sps", nombre: "Tortillería (ejemplo)", producto: "Tortillas", whatsapp: "+504 0000-0011", sucursal: "sps" },
        { id: "desechables", nombre: "Desechables (ejemplo)", producto: "Platos, bolsas y servilletas", whatsapp: "+504 0000-0012", nota: "Pedir el jueves" },
      ],
    },
  },
};
const negocioDemo = id => DEMOS[id] ? cargarNegocio(DEMOS[id].archivo, DEMOS[id].privado) : null;

module.exports = { DEMOS, negocioDemo };
