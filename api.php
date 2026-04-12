<?php
// ============================================================
//  StarsBazaar — API backend
//  Faylni hosting root yoki /public_html ga joylashtiring
// ============================================================

// ── CONFIG (o'zgartiring!) ───────────────────────────────────
define('DB_HOST', 'localhost');
define('DB_NAME', '69cf821c02656_stars_shop');     // ← o'zgartiring
define('DB_USER', '69cf821c02656_stars_shop');     // ← o'zgartiring
define('DB_PASS', 'kI6uW9dT0r');    // ← o'zgartiring
define('DB_CHARSET', 'utf8mb4');

define('BOT_TOKEN', '7463132789:AAF0My042Ps_GSE1sq30ftUSXhg5RlnEj8I');
define('ADMIN_TG_ID', '8178711164');
define('ORDERS_CHAT_ID', '-1002579631278');
define('API_SECRET', 'starsbazaar_secret_2025'); // ← starshop.html dagi bilan bir xil!
// ────────────────────────────────────────────────────────────

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, GET, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, X-API-Secret');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') { http_response_code(200); exit; }

// ── DB ulanish ───────────────────────────────────────────────
function db(): PDO {
    static $pdo = null;
    if ($pdo) return $pdo;
    $dsn = 'mysql:host='.DB_HOST.';dbname='.DB_NAME.';charset='.DB_CHARSET;
    $pdo = new PDO($dsn, DB_USER, DB_PASS, [
        PDO::ATTR_ERRMODE            => PDO::ERRMODE_EXCEPTION,
        PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
        PDO::ATTR_EMULATE_PREPARES   => false,
    ]);
    return $pdo;
}

// ── Jadvallarni yaratish (birinchi ishlaganda) ───────────────
function initDB(): void {
    db()->exec("
        CREATE TABLE IF NOT EXISTS users (
            id          BIGINT PRIMARY KEY,
            username    VARCHAR(100),
            first_name  VARCHAR(100),
            last_name   VARCHAR(100),
            balance     INT NOT NULL DEFAULT 0,
            total_spent INT NOT NULL DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS orders (
            id          VARCHAR(40) PRIMARY KEY,
            user_id     BIGINT NOT NULL,
            cat         VARCHAR(20),
            prod        VARCHAR(200),
            recip       VARCHAR(200),
            price       INT NOT NULL DEFAULT 0,
            stars       INT NOT NULL DEFAULT 0,
            pay_method  VARCHAR(50),
            status      VARCHAR(20) NOT NULL DEFAULT 'wait',
            from_info   VARCHAR(300),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

        CREATE TABLE IF NOT EXISTS settings (
            skey   VARCHAR(100) PRIMARY KEY,
            svalue LONGTEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    ");
}

// ── Yordamchi funksiyalar ────────────────────────────────────
function ok(array $data = []): void {
    echo json_encode(['ok' => true] + $data);
    exit;
}
function err(string $msg, int $code = 400): void {
    http_response_code($code);
    echo json_encode(['ok' => false, 'error' => $msg]);
    exit;
}
function input(): array {
    $raw = file_get_contents('php://input');
    return json_decode($raw, true) ?? [];
}
function checkSecret(): void {
    $h = $_SERVER['HTTP_X_API_SECRET'] ?? '';
    $b = input()['secret'] ?? '';
    if ($h !== API_SECRET && $b !== API_SECRET) err('Unauthorized', 401);
}
function tgSend(string $chatId, string $text, string $parseMode = 'Markdown'): void {
    $url = 'https://api.telegram.org/bot'.BOT_TOKEN.'/sendMessage';
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 8,
        CURLOPT_POSTFIELDS     => json_encode([
            'chat_id'    => $chatId,
            'text'       => $text,
            'parse_mode' => $parseMode,
        ]),
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    ]);
    curl_exec($ch);
    curl_close($ch);
}
function tgSendPhoto(string $chatId, string $photoPath, string $caption): bool {
    $url = 'https://api.telegram.org/bot'.BOT_TOKEN.'/sendPhoto';
    $ch  = curl_init($url);
    curl_setopt_array($ch, [
        CURLOPT_POST           => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_TIMEOUT        => 15,
        CURLOPT_POSTFIELDS     => [
            'chat_id'    => $chatId,
            'photo'      => new CURLFile($photoPath),
            'caption'    => $caption,
            'parse_mode' => 'Markdown',
        ],
    ]);
    $res = curl_exec($ch);
    curl_close($ch);
    $d = json_decode($res, true);
    return $d['ok'] ?? false;
}

// ── Routing ──────────────────────────────────────────────────
try {
    initDB();
} catch (Exception $e) {
    err('DB error: '.$e->getMessage(), 500);
}

$action = $_GET['action'] ?? $_POST['action'] ?? (input()['action'] ?? '');

switch ($action) {

    // ── Foydalanuvchini ro'yxatdan o'tkazish / olish ─────────
    case 'getUser': {
        $d = input();
        $userId = (int)($d['user_id'] ?? 0);
        if (!$userId) err('user_id required');

        $stmt = db()->prepare('SELECT * FROM users WHERE id = ?');
        $stmt->execute([$userId]);
        $user = $stmt->fetch();

        if (!$user) {
            // Yangi foydalanuvchi
            db()->prepare('INSERT INTO users (id, username, first_name, last_name) VALUES (?,?,?,?)')
               ->execute([$userId, $d['username']??'', $d['first_name']??'', $d['last_name']??'']);
            $user = ['id'=>$userId,'username'=>$d['username']??'','first_name'=>$d['first_name']??'',
                     'last_name'=>$d['last_name']??'','balance'=>0,'total_spent'=>0];
        } else {
            // Ma'lumotlarni yangilash
            db()->prepare('UPDATE users SET username=?, first_name=?, last_name=? WHERE id=?')
               ->execute([$d['username']??$user['username'], $d['first_name']??$user['first_name'],
                          $d['last_name']??$user['last_name'], $userId]);
        }

        // Foydalanuvchining zakazlari
        $stmt2 = db()->prepare('SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC');
        $stmt2->execute([$userId]);
        $orders = $stmt2->fetchAll();

        ok(['user' => $user, 'orders' => $orders]);
    }

    // ── Zakaz berish ─────────────────────────────────────────
    case 'createOrder': {
        $d = input();
        $userId  = (int)($d['user_id'] ?? 0);
        $orderId = $d['order_id'] ?? '';
        $cat     = $d['cat'] ?? '';
        $prod    = $d['prod'] ?? '';
        $recip   = $d['recip'] ?? '';
        $price   = (int)($d['price'] ?? 0);
        $stars   = (int)($d['stars'] ?? 0);
        $method  = $d['pay_method'] ?? 'humo';
        $from    = $d['from_info'] ?? '';

        if (!$userId || !$orderId || !$price) err('Majburiy maydonlar yetishmaydi');

        // Foydalanuvchini tekshirish
        $stmt = db()->prepare('SELECT * FROM users WHERE id = ?');
        $stmt->execute([$userId]);
        $user = $stmt->fetch();
        if (!$user) err('Foydalanuvchi topilmadi');

        // Balansni tekshirish (agar kerak bo'lsa kelajakda)
        // Hozir: chek bilan to'lov, balans ishlatilmaydi

        // Zakazni saqlash
        db()->prepare('INSERT INTO orders (id, user_id, cat, prod, recip, price, stars, pay_method, status, from_info) VALUES (?,?,?,?,?,?,?,?,?,?)')
           ->execute([$orderId, $userId, $cat, $prod, $recip, $price, $stars, $method, 'wait', $from]);

        // total_spent ni yangilash
        db()->prepare('UPDATE users SET total_spent = total_spent + ? WHERE id = ?')
           ->execute([$price, $userId]);

        // Telegram ga xabar yuborish
        $msg = "🛒 *YANGI BUYURTMA — Stars Bazaar*\n\n"
             . "📦 Mahsulot: {$prod}\n"
             . "👤 Kimga: {$recip}\n"
             . "💰 Summa: " . number_format($price, 0, '.', ' ') . " uzs\n"
             . "🔖 Buyurtma №: {$orderId}\n"
             . "💳 To'lov: {$method}\n\n"
             . "🙋 Buyurtmachi: {$from}\n"
             . "⏰ Vaqt: " . date('d.m.Y H:i');

        tgSend(ORDERS_CHAT_ID, $msg);
        tgSend(ADMIN_TG_ID, $msg);

        ok(['order_id' => $orderId]);
    }

    // ── Chek rasmini yuborish ────────────────────────────────
    case 'sendChek': {
        if ($_SERVER['REQUEST_METHOD'] !== 'POST') err('POST required');
        $userId  = (int)($_POST['user_id'] ?? 0);
        $orderId = $_POST['order_id'] ?? '';
        $prod    = $_POST['prod'] ?? '';
        $recip   = $_POST['recip'] ?? '';
        $price   = (int)($_POST['price'] ?? 0);
        $from    = $_POST['from_info'] ?? '';

        if (!isset($_FILES['chek']) || $_FILES['chek']['error'] !== 0) err('Fayl yuborilmadi');

        $tmpPath = $_FILES['chek']['tmp_name'];
        $cap = "🛒 *YANGI BUYURTMA — Stars Bazaar*\n\n"
             . "📦 Mahsulot: {$prod}\n"
             . "👤 Kimga: {$recip}\n"
             . "💰 Summa: " . number_format($price, 0, '.', ' ') . " uzs\n"
             . "🔖 Buyurtma №: {$orderId}\n\n"
             . "🙋 Buyurtmachi: {$from}\n"
             . "⏰ Vaqt: " . date('d.m.Y H:i');

        $sent = tgSendPhoto(ORDERS_CHAT_ID, $tmpPath, $cap);
        if (!$sent) tgSend(ORDERS_CHAT_ID, $cap); // fallback

        // Adminga ham chek rasmini yuborish
        $sentAdmin = tgSendPhoto(ADMIN_TG_ID, $tmpPath, $cap);
        if (!$sentAdmin) tgSend(ADMIN_TG_ID, $cap); // fallback

        ok(['sent' => true]);
    }

    // ── Zakaz statusini o'zgartirish (admin) ─────────────────
    case 'updateOrder': {
        checkSecret();
        $d       = input();
        $orderId = $d['order_id'] ?? '';
        $status  = $d['status'] ?? '';

        if (!$orderId || !in_array($status, ['done','cancel','wait'])) err('Noto\'g\'ri ma\'lumot');

        if ($status === 'done') {
            // Zakaz bajarildi — foydalanuvchiga xabar
            $stmt = db()->prepare('SELECT o.*, u.id as uid FROM orders o JOIN users u ON o.user_id=u.id WHERE o.id=?');
            $stmt->execute([$orderId]);
            $order = $stmt->fetch();
            if ($order) {
                $notif = "✅ *Buyurtmangiz bajarildi!*\n\n"
                       . "📦 {$order['prod']}\n"
                       . "👤 {$order['recip']}\n"
                       . "🔖 #{$orderId}\n\n"
                       . "⭐ StarsBazaar — xizmatdan foydalanganingiz uchun rahmat!";
                tgSend((string)$order['uid'], $notif);
            }
        }

        db()->prepare('UPDATE orders SET status=? WHERE id=?')->execute([$status, $orderId]);
        ok(['updated' => true]);
    }

    // ── Zakazni o'chirish (admin) ────────────────────────────
    case 'deleteOrder': {
        checkSecret();
        $d = input();
        $orderId = $d['order_id'] ?? '';
        if (!$orderId) err('order_id required');
        db()->prepare('DELETE FROM orders WHERE id=?')->execute([$orderId]);
        ok(['deleted' => true]);
    }

    // ── Barcha zakazlarni olish (admin) ──────────────────────
    case 'getOrders': {
        checkSecret();
        $status = $_GET['status'] ?? 'all';
        if ($status === 'all') {
            $stmt = db()->query('SELECT o.*, u.username, u.first_name FROM orders o LEFT JOIN users u ON o.user_id=u.id ORDER BY o.created_at DESC');
        } else {
            $stmt = db()->prepare('SELECT o.*, u.username, u.first_name FROM orders o LEFT JOIN users u ON o.user_id=u.id WHERE o.status=? ORDER BY o.created_at DESC');
            $stmt->execute([$status]);
        }
        ok(['orders' => $stmt->fetchAll()]);
    }

    // ── Foydalanuvchi balansini to'ldirish (admin) ───────────
    case 'topupBalance': {
        checkSecret();
        $d      = input();
        $userId = (int)($d['user_id'] ?? 0);
        $amount = (int)($d['amount'] ?? 0);
        if (!$userId || $amount <= 0) err('Noto\'g\'ri ma\'lumot');

        db()->prepare('UPDATE users SET balance = balance + ? WHERE id=?')->execute([$amount, $userId]);
        $stmt = db()->prepare('SELECT balance FROM users WHERE id=?');
        $stmt->execute([$userId]);
        $row = $stmt->fetch();

        // Foydalanuvchiga xabar
        $msg = "💰 *Balans to'ldirildi!*\n\n"
             . "+ " . number_format($amount, 0, '.', ' ') . " uzs\n"
             . "💳 Joriy balans: " . number_format($row['balance'], 0, '.', ' ') . " uzs\n\n"
             . "⭐ StarsBazaar";
        tgSend((string)$userId, $msg);

        ok(['balance' => (int)$row['balance']]);
    }

    // ── Barcha foydalanuvchilar (admin) ──────────────────────
    case 'getUsers': {
        checkSecret();
        $stmt = db()->query('SELECT *, (SELECT COUNT(*) FROM orders WHERE user_id=users.id) as order_count FROM users ORDER BY total_spent DESC');
        ok(['users' => $stmt->fetchAll()]);
    }

    // ── Sozlamalarni saqlash/olish ───────────────────────────
    case 'getSettings': {
        $stmt = db()->query('SELECT skey, svalue FROM settings');
        $rows = $stmt->fetchAll();
        $result = [];
        foreach ($rows as $r) {
            $decoded = json_decode($r['svalue'], true);
            $result[$r['skey']] = $decoded !== null ? $decoded : $r['svalue'];
        }
        ok(['settings' => $result]);
    }

    case 'saveSettings': {
        checkSecret();
        $d = input();
        $data = $d['data'] ?? [];
        $stmt = db()->prepare('INSERT INTO settings (skey, svalue) VALUES (?,?) ON DUPLICATE KEY UPDATE svalue=VALUES(svalue)');
        foreach ($data as $key => $val) {
            $stmt->execute([$key, is_string($val) ? $val : json_encode($val, JSON_UNESCAPED_UNICODE)]);
        }
        ok();
    }

    // ── Dashboard statistika (admin) ─────────────────────────
    case 'getStats': {
        checkSecret();
        $totalRev  = db()->query('SELECT COALESCE(SUM(price),0) as v FROM orders WHERE status != "cancel"')->fetch()['v'];
        $totalOrd  = db()->query('SELECT COUNT(*) as v FROM orders')->fetch()['v'];
        $pendOrd   = db()->query('SELECT COUNT(*) as v FROM orders WHERE status="wait"')->fetch()['v'];
        $totalUsers= db()->query('SELECT COUNT(*) as v FROM users')->fetch()['v'];
        $totalStars= db()->query('SELECT COALESCE(SUM(stars),0) as v FROM orders WHERE cat="stars" AND status!="cancel"')->fetch()['v'];

        // Haftalik zakazlar
        $weekly = db()->query('
            SELECT DATE(created_at) as day, COUNT(*) as cnt, COALESCE(SUM(price),0) as rev
            FROM orders
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY day ASC
        ')->fetchAll();

        // Top mahsulotlar
        $topProds = db()->query('
            SELECT prod, COUNT(*) as cnt, SUM(price) as rev
            FROM orders WHERE status != "cancel"
            GROUP BY prod ORDER BY cnt DESC LIMIT 5
        ')->fetchAll();

        ok([
            'total_revenue' => (int)$totalRev,
            'total_orders'  => (int)$totalOrd,
            'pending_orders'=> (int)$pendOrd,
            'total_users'   => (int)$totalUsers,
            'total_stars'   => (int)$totalStars,
            'weekly'        => $weekly,
            'top_products'  => $topProds,
        ]);
    }

    default:
        err('Noma\'lum action: '.$action, 404);
}
