import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.attribute.BasicFileAttributes;
import java.time.DateTimeException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneOffset;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.Locale;

public class BackupRetentionPlanner {
    record Backup(String name, Instant modified, long bytes) {
        LocalDate date() {
            return modified.atZone(ZoneOffset.UTC).toLocalDate();
        }
    }

    static List<Backup> scan(Path folder) throws IOException {
        if (!Files.isDirectory(folder, LinkOption.NOFOLLOW_LINKS)) {
            throw new IllegalArgumentException("Input must be a real directory, not a symbolic link.");
        }
        List<Backup> backups = new ArrayList<>();
        try (DirectoryStream<Path> entries = Files.newDirectoryStream(folder)) {
            for (Path file : entries) {
                String name = file.getFileName().toString();
                String lower = name.toLowerCase(Locale.ROOT);
                if (!lower.endsWith(".zip") && !lower.endsWith(".bak")) {
                    continue;
                }
                BasicFileAttributes attributes = Files.readAttributes(
                        file, BasicFileAttributes.class, LinkOption.NOFOLLOW_LINKS);
                if (attributes.isRegularFile()) {
                    backups.add(new Backup(name, attributes.lastModifiedTime().toInstant(), attributes.size()));
                }
            }
        }
        return backups;
    }

    static List<Backup> sample(LocalDate asOf) {
        List<Backup> backups = new ArrayList<>();
        int[] ages = {1, 7, 45, 46, 70};
        for (int i = 0; i < ages.length; i++) {
            Instant modified = asOf.minusDays(ages[i]).atTime(12, 0).toInstant(ZoneOffset.UTC);
            backups.add(new Backup("sample-" + (i + 1) + ".zip", modified, 10L * 1024 * 1024));
        }
        return backups;
    }

    static void report(List<Backup> backups, int maxAge, int minimumCopies, LocalDate asOf) {
        backups.sort(Comparator.comparing(Backup::modified).reversed().thenComparing(Backup::name));
        int ordinaryRank = 0;
        int kept = 0;
        int review = 0;
        int future = 0;
        long reviewBytes = 0;
        System.out.printf("As of: %s (UTC dates)%nPolicy: age <= %d days OR newest %d files%n%n",
                asOf, maxAge, minimumCopies);
        for (Backup backup : backups) {
            long age = ChronoUnit.DAYS.between(backup.date(), asOf);
            String status;
            String reason;
            if (age < 0) {
                status = "KEEP_CHECK_DATE";
                reason = "Future UTC date; excluded from the minimum-copy count";
                future++;
                kept++;
            } else {
                ordinaryRank++;
                if (ordinaryRank <= minimumCopies || age <= maxAge) {
                    status = "KEEP";
                    reason = ordinaryRank <= minimumCopies ? "Protected newest file" : "Within age limit";
                    kept++;
                } else {
                    status = "REVIEW";
                    reason = "Outside age limit and protected newest files";
                    review++;
                    reviewBytes += backup.bytes();
                }
            }
            System.out.printf("%s | %s | date=%s | age=%d days | %.2f MiB | %s%n",
                    status, backup.name(), backup.date(), age, backup.bytes() / 1048576.0, reason);
        }
        System.out.printf(Locale.ROOT,
                "%nFiles: %d | Keep: %d | Review: %d | Future dates: %d%nReview size: %.2f MiB%n",
                backups.size(), kept, review, future, reviewBytes / 1048576.0);
        if (ordinaryRank < minimumCopies) {
            System.out.println("Notice: fewer non-future files exist than the requested minimum.");
        }
        System.out.println("Planning only: no files were changed or deleted.");
    }

    public static void main(String[] args) {
        if (args.length == 1 && args[0].equals("--help")) {
            usage();
            return;
        }
        try {
            if (args.length < 1 || args.length > 4) {
                throw new IllegalArgumentException("Provide a folder or --demo, then up to three settings.");
            }
            int maxAge = args.length > 1 ? Integer.parseInt(args[1]) : 30;
            int minimumCopies = args.length > 2 ? Integer.parseInt(args[2]) : 3;
            LocalDate asOf = args.length > 3 ? LocalDate.parse(args[3]) : LocalDate.now(ZoneOffset.UTC);
            if (maxAge < 0 || minimumCopies < 1) {
                throw new IllegalArgumentException("Max age must be >= 0 and minimum copies must be >= 1.");
            }
            boolean demo = args[0].equals("--demo");
            List<Backup> backups = demo ? sample(asOf) : scan(Path.of(args[0]));
            if (demo) {
                System.out.println("DEMO: fictional file metadata; no folder is scanned.\n");
            }
            report(backups, maxAge, minimumCopies, asOf);
        } catch (IOException | IllegalArgumentException | DateTimeException | SecurityException error) {
            System.err.println("Error: " + error.getMessage());
            usage();
            System.exit(1);
        }
    }

    static void usage() {
        System.out.println("Usage: java BackupRetentionPlanner.java <folder|--demo> [max-age-days] [minimum-copies] [YYYY-MM-DD]");
        System.out.println("Defaults: 30 days, 3 newest files, current UTC date. Use --help for this message.");
    }
}
