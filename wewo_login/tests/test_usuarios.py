import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import logs
import seguridad
import usuarios


class UsuariosTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.archivo_usuarios_original = usuarios.ARCHIVO_USUARIOS
        self.archivo_log_original = logs.ARCHIVO_LOG
        self.intentos_original = usuarios.INTENTOS_FALLIDOS.copy()
        self.bloqueos_original = usuarios.BLOQUEOS.copy()

        usuarios.ARCHIVO_USUARIOS = Path(self.tmp.name) / "usuarios.txt"
        logs.ARCHIVO_LOG = Path(self.tmp.name) / "log.txt"
        usuarios.INTENTOS_FALLIDOS.clear()
        usuarios.BLOQUEOS.clear()

    def tearDown(self):
        usuarios.ARCHIVO_USUARIOS = self.archivo_usuarios_original
        logs.ARCHIVO_LOG = self.archivo_log_original
        usuarios.INTENTOS_FALLIDOS.clear()
        usuarios.INTENTOS_FALLIDOS.update(self.intentos_original)
        usuarios.BLOQUEOS.clear()
        usuarios.BLOQUEOS.update(self.bloqueos_original)
        self.tmp.cleanup()

    def crear_usuario_de_prueba(self, nombre="ivan", contraseña="Clave123!"):
        salt = "salt"
        hash_guardado = seguridad.hash_contraseña(contraseña, salt)
        return usuarios.crear_registro_usuario(
            nombre,
            salt,
            hash_guardado,
            rol="usuario"
        )

    def test_guardar_y_leer_usuarios_formato_actual(self):
        registro = self.crear_usuario_de_prueba()

        usuarios.guardar_usuarios([registro])
        leidos = usuarios.leer_usuarios()

        self.assertEqual(len(leidos), 1)
        self.assertEqual(leidos[0]["usuario"], "ivan")
        self.assertEqual(leidos[0]["intentos_fallidos"], 0)
        self.assertEqual(leidos[0]["bloqueado_hasta"], usuarios.SIN_BLOQUEO)

    def test_lee_registro_viejo_de_tres_campos(self):
        usuarios.ARCHIVO_USUARIOS.write_text(
            "admin + salt + hash\n",
            encoding="utf-8"
        )

        leidos = usuarios.leer_usuarios()

        self.assertEqual(leidos[0]["usuario"], "admin")
        self.assertEqual(leidos[0]["rol"], "admin")
        self.assertEqual(leidos[0]["fecha_creacion"], "Desconocida")

    def test_bloqueo_se_persiste_en_archivo(self):
        usuarios.guardar_usuarios([self.crear_usuario_de_prueba()])

        with patch("builtins.print"):
            usuarios.registrar_intento_fallido("ivan")
            usuarios.registrar_intento_fallido("ivan")
            usuarios.registrar_intento_fallido("ivan")

        datos = usuarios.obtener_usuario("ivan")
        self.assertEqual(datos["intentos_fallidos"], usuarios.MAX_INTENTOS)
        self.assertNotEqual(datos["bloqueado_hasta"], usuarios.SIN_BLOQUEO)
        with patch("builtins.print"):
            self.assertTrue(usuarios.usuario_bloqueado("ivan"))

    def test_bloqueo_vencido_limpia_estado(self):
        vencido = datetime.now() - timedelta(seconds=1)
        registro = self.crear_usuario_de_prueba()
        registro["intentos_fallidos"] = usuarios.MAX_INTENTOS
        registro["bloqueado_hasta"] = usuarios.formatear_fecha(vencido)
        usuarios.guardar_usuarios([registro])

        self.assertFalse(usuarios.usuario_bloqueado("ivan"))

        datos = usuarios.obtener_usuario("ivan")
        self.assertEqual(datos["intentos_fallidos"], 0)
        self.assertEqual(datos["bloqueado_hasta"], usuarios.SIN_BLOQUEO)

    def test_login_correcto_limpia_intentos_y_actualiza_ultimo_login(self):
        registro = self.crear_usuario_de_prueba()
        registro["intentos_fallidos"] = 2
        usuarios.guardar_usuarios([registro])

        with patch("builtins.input", return_value="ivan"), patch(
            "usuarios.getpass",
            return_value="Clave123!"
        ), patch("builtins.print"):
            confirmacion, usuario = usuarios.iniciar_sesion()

        datos = usuarios.obtener_usuario("ivan")
        self.assertTrue(confirmacion)
        self.assertEqual(usuario, "ivan")
        self.assertEqual(datos["intentos_fallidos"], 0)
        self.assertNotEqual(datos["ultimo_login"], "Nunca")


if __name__ == "__main__":
    unittest.main()
