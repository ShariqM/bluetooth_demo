#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <gio/gio.h>
#include <glib.h>
#include <iostream>
#include <string>

#define SERVICE_UUID        "12345678-1234-5678-1234-56789abcdef0"
#define CHARACTERISTIC_UUID "12345678-1234-5678-1234-56789abcdef1"

static GMainLoop *main_loop = nullptr;
static guint registration_id = 0;

static gboolean register_application(GDBusConnection *connection) {
    GVariantBuilder builder;
    g_variant_builder_init(&builder, G_VARIANT_TYPE("a{sv}"));

    GVariant *app_variant = g_variant_new("(oa{sv})", "/", &builder);
    g_variant_builder_clear(&builder);

    GError *error = nullptr;
    if (!g_dbus_connection_call_sync(connection,
                                     "org.bluez",
                                     "/org/bluez/hci0",
                                     "org.bluez.GattManager1",
                                     "RegisterApplication",
                                     app_variant,
                                     nullptr,
                                     G_DBUS_CALL_FLAGS_NONE,
                                     -1,
                                     nullptr,
                                     &error)) {
        std::cerr << "Failed to register application: " << error->message << std::endl;
        g_error_free(error);
        return FALSE;
    }

    std::cout << "Application registered" << std::endl;
    return TRUE;
}

static void on_bus_acquired(GDBusConnection *connection, const gchar *name, gpointer user_data) {
    std::cout << "Bus acquired: " << name << std::endl;

    if (register_application(connection)) {
        std::cout << "BLE GATT server started. Service UUID: " << SERVICE_UUID << std::endl;
    } else {
        g_main_loop_quit(main_loop);
    }
}

static void on_name_acquired(GDBusConnection *connection, const gchar *name, gpointer user_data) {
    std::cout << "Name acquired: " << name << std::endl;
}

static void on_name_lost(GDBusConnection *connection, const gchar *name, gpointer user_data) {
    std::cout << "Name lost" << std::endl;
    g_main_loop_quit(main_loop);
}

int main() {
    main_loop = g_main_loop_new(nullptr, FALSE);

    registration_id = g_bus_own_name(G_BUS_TYPE_SYSTEM,
                                     "org.example.BleServer",
                                     G_BUS_NAME_OWNER_FLAGS_NONE,
                                     on_bus_acquired,
                                     on_name_acquired,
                                     on_name_lost,
                                     nullptr,
                                     nullptr);

    g_main_loop_run(main_loop);

    g_bus_unown_name(registration_id);
    g_main_loop_unref(main_loop);

    return 0;
}
