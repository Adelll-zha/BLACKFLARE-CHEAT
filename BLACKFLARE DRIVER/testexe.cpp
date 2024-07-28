#include <interception.h>
#include <cstring>
#include <windows.h>


int main() {
    InterceptionContext context = interception_create_context();

    // Crée un objet InterceptionMouseStroke pour déplacer le curseur
    InterceptionMouseStroke stroke;
    stroke.state = INTERCEPTION_FILTER_MOUSE_MOVE;
    stroke.flags = 0;
    stroke.rolling = 0;
    stroke.x = -200;
    stroke.y = -100;
    stroke.information = 0;

    // Copie les données de stroke dans le premier élément de strokes
    InterceptionStroke strokes[1];
    memcpy(strokes, &stroke, sizeof(strokes));

    // Envoie le mouvement du curseur
    interception_send(context, INTERCEPTION_MOUSE(0), strokes, 1);

    // Libère les ressources
    interception_destroy_context(context);
    
}