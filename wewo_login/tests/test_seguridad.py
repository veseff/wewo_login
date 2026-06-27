import unittest

import seguridad


class SeguridadTests(unittest.TestCase):
    def test_validar_usuario_acepta_formato_esperado(self):
        self.assertTrue(seguridad.validar_usuario("ivan_123"))
        self.assertTrue(seguridad.validar_usuario("user-name"))

    def test_validar_usuario_rechaza_formato_invalido(self):
        self.assertFalse(seguridad.validar_usuario("ab"))
        self.assertFalse(seguridad.validar_usuario("usuario con espacios"))
        self.assertFalse(seguridad.validar_usuario("usuario!"))

    def test_validar_contraseña_exige_complejidad(self):
        self.assertTrue(seguridad.validar_contraseña("Clave123!"))
        self.assertFalse(seguridad.validar_contraseña("clave123!"))
        self.assertFalse(seguridad.validar_contraseña("Claveclave!"))
        self.assertFalse(seguridad.validar_contraseña("Clave123"))

    def test_hash_y_verificacion_pbkdf2(self):
        salt = seguridad.generar_salt()
        hash_guardado = seguridad.hash_contraseña("Clave123!", salt)

        self.assertTrue(
            seguridad.verificar_contraseña("Clave123!", salt, hash_guardado)
        )
        self.assertFalse(
            seguridad.verificar_contraseña("Otra123!", salt, hash_guardado)
        )

    def test_hash_pbkdf2_corrupto_no_rompe(self):
        self.assertFalse(
            seguridad.verificar_contraseña(
                "Clave123!",
                "salt",
                "pbkdf2_sha256$abc$deadbeef"
            )
        )


if __name__ == "__main__":
    unittest.main()
