/**
 * Simple function to add user role class to body
 * @param {string} role - The user's role (e.g., 'admin', 'user', 'moderator')
 */
export function applyUserRoleClass(role) {
    if (role) {
        // Remove any existing role classes
        document.body.classList.remove(
            ...Array.from(document.body.classList).filter(cls => cls.startsWith('role-'))
        );
        // Add new role class
        document.body.classList.add(`role-${role}`);
        console.log(`User role set: ${role}`);
    } else {
        // Remove any role classes when user is not set
        document.body.classList.remove(
            ...Array.from(document.body.classList).filter(cls => cls.startsWith('role-'))
        );
    }
}
