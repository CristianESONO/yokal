from django.shortcuts import render


def cgu(request):
    return render(request, 'legal/cgu.html')


def privacy(request):
    return render(request, 'legal/privacy.html')


def faq(request):
    faqs = [
        {
            'q': 'Comment créer mon programme de fidélité ?',
            'a': 'Inscrivez-vous, connectez-vous au dashboard, puis allez dans Programmes > Créer un programme. '
                 'Définissez le nombre de tampons, la récompense et vos couleurs.',
        },
        {
            'q': 'Comment mes clients obtiennent-ils leur carte ?',
            'a': 'Partagez le QR code d\'inscription de votre programme. Vos clients scannent le code, '
                 's\'inscrivent en 30 secondes et peuvent ajouter la carte à Google Wallet.',
        },
        {
            'q': 'Comment ajouter un tampon en caisse ?',
            'a': 'Utilisez le Scanner QR dans le dashboard, ou le bouton +1 Tampon dans la liste Clients. '
                 'Vous pouvez aussi intégrer l\'API publique à votre caisse.',
        },
        {
            'q': 'Google Wallet ne fonctionne pas, que faire ?',
            'a': 'Vérifiez que votre logo de programme est bien uploadé (format PNG/JPG). '
                 'Le client doit cliquer sur « Ajouter à Google Wallet » depuis sa carte digitale.',
        },
        {
            'q': 'Puis-je avoir plusieurs programmes ?',
            'a': 'Oui, vous pouvez créer plusieurs programmes de fidélité et basculer entre eux depuis le dashboard.',
        },
        {
            'q': 'Comment inviter mon équipe ?',
            'a': 'Allez dans Équipe > Inviter un membre. Il recevra un lien pour rejoindre votre commerce '
                 'et pourra scanner les QR codes en caisse.',
        },
        {
            'q': 'Comment utiliser l\'API publique ?',
            'a': 'Activez votre clé API dans Paramètres > API. Utilisez l\'en-tête Authorization: Bearer <clé> '
                 'pour intégrer Yokalma à votre caisse ou CRM.',
        },
        {
            'q': 'Mes données sont-elles sécurisées ?',
            'a': 'Oui. Vos données sont hébergées de manière sécurisée. Consultez notre Politique de confidentialité '
                 'pour plus de détails.',
        },
    ]
    return render(request, 'legal/faq.html', {'faqs': faqs})
