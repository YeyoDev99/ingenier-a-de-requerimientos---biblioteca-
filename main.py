"""
DEMO del diagrama UML - Sistema de Biblioteca.
================================================
Este archivo muestra, paso a paso, como se usan las clases del diagrama.
Si entiendes este main, entiendes el diagrama.

Relacion con el diagrama:
  Book (abstracta) <--- hereda --- BookItem (entity)
  Book 1..* ---wrote--- 1..* Author
  Catalog (1) ---records--- (*) BookItem
  Library (1) <>--- (*) Account  [agregacion]
  Library (1) <*--- Catalog      [composicion]
  Patron --- tiene un --- Account (rol 'account')
  Catalog realiza Search y Manage (interface)
  Patron usa Search, Librarian usa Search y Manage (dependencia use)

Para ejecutar:  python main.py
"""
from datetime import date
from biblioteca import (
    Library, Author, BookItem, Account, AccountState, Patron, Librarian,
)


def separador(titulo: str) -> None:
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


def paso_1_crear_biblioteca() -> Library:
    separador("PASO 1: Crear la Biblioteca (y su Catalogo por composicion)")
    print("En el diagrama: Library <diamante-negro>--- Catalog = COMPOSICION.")
    print("Traduccion: el Catalogo NO puede existir sin la Biblioteca.")
    print("En codigo: al hacer Library(...), ella misma crea su Catalog.\n")

    biblio = Library(name="Biblioteca Central", address="Av. Principal 123")
    print(f"Biblioteca creada: {biblio.name}")
    print(f"Catalogo automatico: {biblio.catalog}")
    print(f"Cuentas al inicio: {len(biblio.accounts)} (agregacion, empieza vacia)")
    return biblio


def paso_2_crear_libros(biblio: Library) -> tuple[Author, BookItem]:
    separador("PASO 2: Crear Autor y Ejemplar (herencia + wrote)")
    print("En el diagrama:")
    print("  - Book es 'abstract class' -> no se instancia directo.")
    print("  - BookItem hereda de Book (flecha generalizacion).")
    print("  - Book 1..* ---wrote--- 1..* Author (muchos a muchos).")
    print("Traduccion: creamos un BookItem concreto y lo unimos a un Author.\n")

    autor = Author(name="Gabriel Garcia Marquez", biography="Escritor colombiano")
    print(f"Autor creado: {autor.name} | libros suyos: {len(autor.books)}")

    ejemplar = BookItem(
        title="Cien anios de soledad",
        summary="Novela realista magica",
        publisher="Sudamericana",
        publication_date=date(1967, 5, 30),
        number_of_pages=471,
        language="ES",
        isbn="978-3-16-148410-0",
        barcode="B-0001",
        tag="RFID-0001",
        is_reference_only=False,
        catalog=biblio.catalog,  # asociacion 'records': el Catalog registra el ejemplar
    )
    print(f"Ejemplar creado: '{ejemplar.title}' con codigo {ejemplar.barcode}")
    print(f"Registrado en catalogo? {ejemplar in biblio.catalog.items}")
    print(f"Total en catalogo: {len(biblio.catalog.items)}")

    # Unir ambos lados de la relacion 'wrote'
    autor.write(ejemplar)
    print("\nDespues de autor.write(ejemplar):")
    print(f"  - El libro tiene {len(ejemplar.authors)} autor(es): {[a.name for a in ejemplar.authors]}")
    print(f"  - El autor tiene {len(autor.books)} libro(s): {[b.title for b in autor.books]}")
    return autor, ejemplar


def paso_3_buscar(biblio: Library) -> None:
    separador("PASO 3: Buscar libros (interfaces Search / Manage)")
    print("En el diagrama: Catalog - - -|> Search y Manage (interface realization).")
    print("Traduccion: el Catalog SABE buscar y gestionar, porque implementa esas interfaces.\n")

    por_titulo = biblio.catalog.search_by_title("cien")
    print(f"Buscar por titulo 'cien' -> {len(por_titulo)} resultado(s): {[b.title for b in por_titulo]}")

    por_autor = biblio.catalog.search_by_author("marquez")
    print(f"Buscar por autor 'marquez' -> {len(por_autor)} resultado(s)")

    por_isbn = biblio.catalog.search_by_isbn("978-3-16-148410-0")
    print(f"Buscar por ISBN exacto -> {len(por_isbn)} resultado(s)")


def paso_4_prestamos(biblio: Library, ejemplar: BookItem) -> Account:
    separador("PASO 4: Crear Cuenta y prestar (multiplicidad 0..12 y 0..3)")
    print("En el diagrama: Account ---borrowed 0..12--- BookItem")
    print("                Account ---reserved 0..3 --- BookItem")
    print("Traduccion: una cuenta puede prestar maximo 12 y reservar maximo 3.\n")

    # Agregacion: la cuenta se crea FUERA y luego se agrega a la biblioteca
    cuenta = Account(number="A-001", opened=date.today(), state=AccountState.ACTIVE)
    print(f"Cuenta creada fuera de la biblioteca: {cuenta}")
    biblio.add_account(cuenta)
    print(f"Cuenta agregada a {biblio.name}. Ahora tiene {len(biblio.accounts)} cuenta(s).")

    cuenta.borrow(ejemplar)
    print(f"\nPrestamo OK: '{ejemplar.title}' prestado a cuenta {cuenta.number}")
    print(f"Prestados ahora: {len(cuenta.borrowed)} / 12")
    print(f"Historial de la cuenta: {cuenta.history}")
    return cuenta


def paso_5_personas(biblio: Library, cuenta: Account, ejemplar: BookItem) -> None:
    separador("PASO 5: Patron y Bibliotecario (asociacion 'account' + uso)")
    print("En el diagrama:")
    print("  - Patron ---- tiene un ---- Account (etiqueta 'account').")
    print("  - Patron - -<<use>>- -> Search (solo la USA, no la guarda).")
    print("  - Librarian - -<<use>>- -> Search y Manage.\n")

    patron = Patron(name="Ana Torres", address="Calle 1", account=cuenta)
    print(f"Patron creado: {patron.name}, su cuenta es: {patron.account.number}")

    # El patron usa el catalogo SOLO a traves de la interfaz Search
    resultados = patron.search(biblio.catalog, "cien")
    print(f"{patron.name} busca 'cien' y encuentra: {[b.title for b in resultados]}")

    bibliotecario = Librarian(name="Luis Perez", address="Calle 2", position="Jefe")
    print(f"\nBibliotecario creado: {bibliotecario.name} ({bibliotecario.position})")

    # El bibliotecario registra un libro nuevo usando la interfaz Manage
    nuevo = BookItem(
        title="El amor en los tiempos del colera",
        summary="Novela",
        publisher="Oveja Negra",
        publication_date=date(1985, 1, 1),
        number_of_pages=496,
        language="ES",
        isbn="978-0-307-38026-6",
        barcode="B-0002",
        tag="RFID-0002",
    )
    bibliotecario.register_book(biblio.catalog, nuevo)
    print(f"{bibliotecario.name} registro '{nuevo.title}' con Manage.")
    print(f"Catalogo ahora tiene {len(biblio.catalog.items)} ejemplares.")

    # Devolver el primer prestamo para dejar todo limpio
    cuenta.return_item(ejemplar)
    print(f"\nSe devolvio '{ejemplar.title}'. Prestados ahora: {len(cuenta.borrowed)}")


def paso_6_agregacion_vs_composicion(biblio: Library, cuenta: Account) -> None:
    separador("PASO 6: Diferencia AGREGACION vs COMPOSICION (clave del examen)")
    print("AGREGACION (Library <>--- Account): si saco la cuenta de la")
    print("biblioteca, la cuenta SIGUE existiendo.")
    biblio.remove_account(cuenta)
    print(f"  -> Quite la cuenta. Biblioteca tiene {len(biblio.accounts)} cuentas.")
    print(f"  -> Pero la cuenta {cuenta.number} sigue viva con {len(cuenta.history)} movimientos.")

    print("\nCOMPOSICION (Library <*>--- Catalog): si muere la biblioteca,")
    print("muere su catalogo. Por eso el Catalog solo se crea dentro de Library.")
    print(f"  -> El catalogo pertenece a: {biblio.catalog.library.name}")


def main() -> None:
    print("BIBLIOTECA - Demo del diagrama UML paso a paso")
    biblio = paso_1_crear_biblioteca()
    _, ejemplar = paso_2_crear_libros(biblio)
    paso_3_buscar(biblio)
    cuenta = paso_4_prestamos(biblio, ejemplar)
    paso_5_personas(biblio, cuenta, ejemplar)
    paso_6_agregacion_vs_composicion(biblio, cuenta)

    separador("FIN: Todo funciono = el diagrama esta bien implementado")


if __name__ == "__main__":
    main()
