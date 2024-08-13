from cryptography.fernet import Fernet

from app.config import settings


class EncryptionManager:
    def __init__(self):
        """
        Инициализирует менеджер шифрования с ключом, загружаемым из переменной окружения.
        """
        self.key = settings.ENCRYPTION_KEY
        if not self.key:
            raise ValueError("ENCRYPTION_KEY environment variable not set.")
        self.cipher = Fernet(self.key)  # Создание объекта Fernet

    def encrypt(self, plaintext: str) -> str:
        """
        Шифрует текстовое сообщение.

        :param plaintext: Обычное текстовое сообщение.
        :return: Зашифрованное сообщение в формате base64.
        """
        encrypted_text = self.cipher.encrypt(plaintext.encode())
        return encrypted_text.decode()  # Возвращаем в виде строки

    def decrypt(self, encrypted_text: str) -> str:
        """
        Расшифровывает текстовое сообщение.

        :param encrypted_text: Зашифрованное сообщение в формате base64.
        :return: Расшифрованное сообщение.
        """
        decrypted_text = self.cipher.decrypt(encrypted_text.encode())
        return decrypted_text.decode()  # Возвращаем в виде строки


# Создание экземпляра менеджера шифрования
encryption_manager = EncryptionManager()


def decrypt(encrypted_text: str) -> str:
    """
    Расшифровывает зашифрованное сообщение, используя менеджер шифрования.

    Эта функция оборачивает метод `decrypt` класса `EncryptionManager` и предоставляет простой интерфейс
    для расшифровки текста.

    :param encrypted_text: Зашифрованное сообщение в формате base64. Ожидается, что это строка, полученная
                           после шифрования текста.
    :return: Расшифрованное сообщение в виде строки. Это исходный текст до шифрования.
    """
    return encryption_manager.decrypt(encrypted_text)

