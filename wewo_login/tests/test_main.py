import importlib
import unittest
from unittest.mock import patch


class MainTests(unittest.TestCase):
    def test_importar_main_no_ejecuta_menu(self):
        with patch("builtins.input") as input_mock:
            importlib.import_module("main")

        input_mock.assert_not_called()

    def test_main_muestra_opcion_invalida(self):
        import main

        with patch("builtins.input", return_value="x"), patch(
            "builtins.print"
        ) as print_mock:
            main.main()

        print_mock.assert_any_call("Opción inválida")

    def test_procesar_login_exitoso_registra_y_abre_menu(self):
        import main

        with patch("main.iniciar_sesion", return_value=(True, "ivan")), patch(
            "main.registrar_log"
        ) as log_mock, patch("main.menu_usuario") as menu_mock:
            main.procesar_login()

        log_mock.assert_called_once_with("LOGIN EXITOSO - ivan")
        menu_mock.assert_called_once_with("ivan")


if __name__ == "__main__":
    unittest.main()
